import subprocess


class RTSPAudioStream:
    """Read raw PCM audio from an RTSP stream using ffmpeg.

    Purpose:
        Wraps an ffmpeg subprocess to decode RTSP audio into 16-bit PCM bytes.

    Usage:
        stream = RTSPAudioStream(rtsp_url)
        data = stream.read()
        stream.close()
    """

    def __init__(self, rtsp_url, sample_rate=16000, channels=1, chunk_size=16000):
        """Initialize RTSP audio stream wrapper with FFmpeg settings."""
        self.rtsp_url = rtsp_url
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.process = None

    def start(self):
        """Start ffmpeg if needed and return the underlying process handle."""
        if self.process is not None:
            return self.process

        command = [
            "ffmpeg",
            "-loglevel", "error",
            "-i", self.rtsp_url,
            "-vn",
            "-ac", str(self.channels),
            "-ar", str(self.sample_rate),
            "-f", "s16le",
            "pipe:1",
        ]

        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                bufsize=0,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "ffmpeg is required for RTSP audio parsing but was not found in PATH"
            ) from exc

        return self.process

    def read(self, size=None):
        """Read raw audio bytes from the RTSP audio stream."""
        process = self.start()
        if process.stdout is None:
            return b""

        return process.stdout.read(size or self.chunk_size)

    def close(self):
        """Stop the ffmpeg process and release its resources."""
        if self.process is None:
            return

        if self.process.stdout is not None:
            self.process.stdout.close()

        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()

        self.process = None