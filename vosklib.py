import json
import os
from vosk import Model, KaldiRecognizer

class VoskRecognizer:
    """Speech recognition wrapper for the Vosk model.

    Purpose:
        Load a Vosk model and expose a simple process() API for raw audio chunks.

    Usage:
        recognizer = VoskRecognizer(model_path, sample_rate=16000)
        text = recognizer.process(audio_bytes)
    """

    def __init__(self, model_path, sample_rate=16000):
        """Load the Vosk speech recognition model and initialize the recognizer."""
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