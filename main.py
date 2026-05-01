import re
import unicodedata
import sounddevice as sd
import queue
import threading
import time
import subprocess
import argparse


from vosklib import VoskRecognizer
from yamnet import YamnetClassifier
from rtsp_audio import RTSPAudioStream

# =============================
# CONFIG
# =============================
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000
BLOCK_SIZE_BYTES = BLOCK_SIZE * 2  # 2 bytes per sample (int16)
DEVICE_IP = None  # Will be set from command line argument
VALID_YAMNET_LABELS = {
    "gunshot",
    "siren",
    "alarm",
    "glass",
    "scream",
    "shouting",
    "baby cry",
    "dog bark",
    "engine",
    "vehicle",
    "breaking",
}
# Supported languages and their model paths
LANGUAGES = {
    "en": "model/vosk-model-small-en-us-0.15",
    "hi": "model/vosk-model-small-hi-0.22",
    "en-in": "model/vosk-model-small-en-in-0.4",
    "gu": "model/vosk-model-small-gu-0.42",
}

KEYWORDS = {
    "en": ["help", "fire", "stop", "danger", "emergency", "intruder", "attack", "alarm", "police", "ambulance", "thief", "gunshot", "scream", "panic"],
    "hi": ["मदद", "आग", "रुको", "खतरा", "आपातकाल", "घुसपैठिया", "हमला", "अलार्म", "पुलिस", "एम्बुलेंस", "चोर", "गोली", "चीख", "दहशत"],
    "gu": ["મદદ", "આગ", "બંધ કરો", "ખતરો", "કટોકટી", "ઘુસણખોર", "હુમલો", "એલાર્મ", "પોલીસ", "એમ્બ્યુલન્સ", "ચોર", "ગોળી", "ચીસ", "ભય"]
}

ALL_KEYWORDS = {keyword for words in KEYWORDS.values() for keyword in words}

# If True, process all configured languages at once.
RUN_ALL_LANGUAGES = True

# If RUN_ALL_LANGUAGES is False, this language will be used.
LANGUAGE = "hi"

LISTEN_LANGUAGES = list(LANGUAGES.keys()) if RUN_ALL_LANGUAGES else [LANGUAGE]

# =============================
# QUEUES
# =============================
audio_queue = queue.Queue()

# =============================
# INIT MODELS
# =============================
vosk_engines = {
    lang: VoskRecognizer(model_path, SAMPLE_RATE)
    for lang, model_path in LANGUAGES.items()
    if lang in LISTEN_LANGUAGES
}
yamnet_engine = YamnetClassifier()

# =============================
# AUDIO CALLBACK
# =============================
def audio_callback(indata, frames, time, status):
    """Callback invoked by sounddevice for each audio block.

    Converts the incoming audio buffer to bytes and enqueues it for later processing.
    """
    if status:
        print(status)
    # indata is already in the correct format from sounddevice
    audio_queue.put(bytes(indata))


def rtsp_reader(rtsp_url, stop_event):
    """Read raw audio from an RTSP source and enqueue it until stopped.

    The thread runs until the stop_event is set, or the stream ends.
    """
    print(f"RTSP reader started for {rtsp_url}")
    try:
        stream = RTSPAudioStream(rtsp_url, sample_rate=SAMPLE_RATE, channels=1, chunk_size=BLOCK_SIZE_BYTES)
        while not stop_event.is_set():
            data = stream.read(BLOCK_SIZE_BYTES)
            if not data:
                break
            audio_queue.put(data)
    except RuntimeError as exc:
        print(f"RTSP audio source error: {exc}")
        stop_event.set()
    finally:
        if 'stream' in locals():
            stream.close()


# =============================
# WORKER THREAD
# =============================
def audio_worker():
    """Continuously process queued audio blocks from the capture source.

    Speech and sound classification results are forwarded to the decision engine.
    """
    print("Audio worker started...")

    while True:
        data = audio_queue.get()
        

        # ---- VOSK (all languages) ----
        for lang, engine in vosk_engines.items():
            text = engine.process(data)
            if text:
                print(f"[Speech:{lang}] {text}")
                decision_engine(text=text, language=lang)

        # ---- YAMNET ----
        result = yamnet_engine.process(data)
        if result:
            class_id, confidence = result
            label = yamnet_engine.label(class_id)
            print(f"[Sound] ClassID={class_id}, Label={label!r}, Conf={confidence:.2f}")
            if label and ("speech" in label.lower() or "silence" in label.lower()):
                print("[Sound] Skipping decision_engine for speech or silence audio class")
            elif label is not None:
                decision_engine(sound_id=class_id, confidence=confidence, label=label)

# =============================
# DECISION ENGINE
# =============================
def normalize_text(text):
    """Normalize text by stripping punctuation and converting to lowercase."""
    normalized_chars = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat.startswith("L") or cat.startswith("M") or cat.startswith("N") or ch.isspace():
            normalized_chars.append(ch)
        else:
            normalized_chars.append(" ")
    return "".join(normalized_chars).strip().lower()


def decision_engine(text=None, sound_id=None, confidence=None, language=None, label=None):
    """Evaluate speech or sound detections and decide whether to trigger an alert."""
    alert = False

    # Speech trigger
    if text:
        normalized_text = normalize_text(text)

        if language and language in KEYWORDS:
            keywords = KEYWORDS[language]
        else:
            keywords = [keyword for words in KEYWORDS.values() for keyword in words]

        print(f"Checking for keywords in detected text: {normalized_text!r}")
        print(f"Using keywords for language '{language or 'any'}': {keywords}")
        for keyword in keywords:
            if keyword.lower() in normalized_text:
                print(f"🚨 ALERT: Distress word detected! [lang={language or 'any'}]")
                alert = True
                break

    # Sound trigger
    if sound_id is not None:
        if label is not None:
            normalized_label = label.strip().lower()
            if any(valid_label in normalized_label for valid_label in VALID_YAMNET_LABELS):
                print(f"[Sound] Label '{label}' matched alert list; triggering alert without confidence check")
                alert = True
            elif confidence is not None and confidence > 0.6:
                print(f"[Sound] Label '{label}' did not match alert list, but confidence {confidence:.2f} exceeds threshold")
                alert = True
            else:
                print(f"[Sound] Label '{label}' did not match alert list and confidence is too low; no alert")
        else:
            if confidence is not None and confidence > 0.6:
                print("⚠️ Suspicious sound detected (no label available)!")
                alert = True
            else:
                print("[Sound] No label available and confidence is too low; skipping alert")

    if alert:
        trigger_action()

# =============================
# ACTION
# =============================
def trigger_action():
    """Trigger an alert action and optionally send a control command to the configured device."""
    global DEVICE_IP
    print(f"🔴 ACTION: Alarm / Camera / Notification Triggered")
    
    if DEVICE_IP:
        curl_cmd = [
            "curl",
            "--digest",
            "-u", "admin:Admin@123",
            f"http://{DEVICE_IP}/matrix-cgi/ptzcontrol",
            "-d", "action=setpantilt&operation=2&speed=50&state=1"
        ]
        subprocess.run(curl_cmd)
    else:
        print("⚠️ No device IP provided. Skipping curl command.")
    

# =============================
# MAIN
# =============================
def main():
    """Parse command line arguments and start audio capture plus processing threads."""
    global DEVICE_IP
    parser = argparse.ArgumentParser(description="Feed Vosk and YAMNet from microphone or RTSP audio")
    parser.add_argument("--rtsp-url", help="RTSP stream URL to decode and analyze")
    parser.add_argument("--device-ip", help="IP address of the device to control (e.g., 192.168.111.55)")
    args = parser.parse_args()

    DEVICE_IP = args.device_ip

    print("Starting system...")

    stop_event = threading.Event()

    worker = threading.Thread(target=audio_worker, daemon=True)
    worker.start()

    source_thread = None

    try:
        if args.rtsp_url:
            source_thread = threading.Thread(
                target=rtsp_reader,
                args=(args.rtsp_url, stop_event),
                daemon=True,
            )
            source_thread.start()
            print("System running on RTSP stream... Press Ctrl+C to stop.")
            while source_thread.is_alive():
                time.sleep(0.5)
        else:
            stream = sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                dtype='int16',
                channels=1,
                callback=audio_callback
            )

            with stream:
                print("System running on microphone... Press Ctrl+C to stop.")
                while True:
                    time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()

if __name__ == "__main__":
    main()
