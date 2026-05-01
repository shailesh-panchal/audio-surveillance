import json
import os
from vosk import Model, KaldiRecognizer

class VoskRecognizer:
    def __init__(self, model_path, sample_rate=16000):
        if not os.path.exists(model_path):
            raise ValueError(f"Model path {model_path} does not exist. Please download the required model from https://alphacephei.com/vosk/models")
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, sample_rate)

    def process(self, audio_bytes):
        """
        Process incoming audio chunk
        Returns detected text or None
        """
        if self.recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "")
            return text if text else None
        return None