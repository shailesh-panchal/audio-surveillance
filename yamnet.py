import csv
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

class YamnetClassifier:
    """Sound classification wrapper for the Yamnet model.

    Purpose:
        Buffer raw PCM audio bytes, classify them with Yamnet, and expose labels.

    Usage:
        classifier = YamnetClassifier()
        result = classifier.process(audio_bytes)
        if result:
            class_id, confidence = result
            label = classifier.label(class_id)
    """

    def __init__(self):
        """Load the Yamnet model and initialize audio buffering and label mapping."""
        self.model = hub.load("https://tfhub.dev/google/yamnet/1")
        self.buffer = b''
        self.sample_rate = 16000
        self.class_map = self._load_class_map()

    def _load_class_map(self):
        """Load Yamnet class labels from the model asset."""
        class_map_path = self.model.class_map_path()
        if hasattr(class_map_path, 'numpy'):
            class_map_path = class_map_path.numpy().decode('utf-8')

        with open(class_map_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            return [row[2] for row in reader if len(row) >= 3]

    def label(self, class_id):
        """Get the human-readable label for a class ID."""
        if 0 <= class_id < len(self.class_map):
            return self.class_map[class_id]
        return None

    def process(self, audio_bytes):
        """
        Accumulate raw audio and classify it using Yamnet.

        Returns (class_id, confidence) when a segment is classified, or None if
        more audio data is required.
        """
        self.buffer += audio_bytes

        if len(self.buffer) >= self.sample_rate * 2:
            audio_np = np.frombuffer(self.buffer, dtype=np.int16).astype(np.float32) / 32768.0
            self.buffer = b''

            scores, embeddings, spectrogram = self.model(audio_np)
            scores_np = scores.numpy()

            mean_scores = np.mean(scores_np, axis=0)
            class_id = int(np.argmax(mean_scores))
            confidence = float(mean_scores[class_id])

            return class_id, confidence

        return None