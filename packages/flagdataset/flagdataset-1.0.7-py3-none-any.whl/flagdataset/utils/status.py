import threading

from .bytes_format import format_bytes
from .speed_monitor import speed_monitor


def format_seconds(seconds):
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours}h{minutes}m{seconds}s"


class Status:

    def __init__(self):
        self._download_size = 0
        self._required_size = 0
        self._check_size = 0
        self._lock = threading.Lock()

    def download_add_size(self, size):
        with self._lock:
            self._download_size += size

    def required_add_size(self, size):
        with self._lock:
            self._required_size += size

    def check_add_size(self, size):
        with self._lock:
            self._check_size += size

    @property
    def remaining_size(self):
        size_ = -(self._check_size + self._download_size - self._required_size)
        return size_

    @property
    def download_size(self):
        size_ = self._download_size + self._check_size
        return size_

    @property
    def required_size(self):
        size_ = self._required_size
        return size_

    def __repr__(self):
        return (
            f"download_size: {self._download_size}, "
            f"required_size: {self._required_size}, "
            f"check_size: {self._check_size}, "
            f"remaining_size: {self.remaining_size}"
        )

    def __str__(self):

        download_speed = speed_monitor.download_speed
        required_time = "0h0m0s"
        if self._download_size > 0 and download_speed > 0:
            second = self.remaining_size / download_speed
            required_time = format_seconds(second)

        if self.required_size > 0:
            progress = f"{self.download_size / self.required_size * 100:.2f}"
        else:
            progress = "unknown"

        completed = (
            f"{format_bytes(self.download_size)}/{format_bytes(self.required_size)}"
        )

        return (
            f"progress: {progress}%, "
            f"completed: {completed}, "
            f"required: {required_time}"
        )


status_manager = Status()
