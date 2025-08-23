import threading
import time

import psutil


class SpeedMonitor:

    def __init__(self):
        self._lock = threading.Lock()
        self._download_speed = 0

    def update_download_speed(self, down_speed):
        with self._lock:
            self._download_speed = down_speed

    @property
    def download_speed(self):
        return self._download_speed


speed_monitor = SpeedMonitor()


def format_speed(speed_bytes_per_second):
    """将字节/秒转换为合适的单位（KB/s、MB/s、GB/s）"""
    units = ["B/s", "KB/s", "MB/s", "GB/s"]
    index = 0
    while speed_bytes_per_second >= 1024 and index < len(units) - 1:
        speed_bytes_per_second /= 1024
        index += 1
    return f"{speed_bytes_per_second:.1f}{units[index]}"


def network_speed():

    # 获取初始数据
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv

    time.sleep(1)

    net_io_new = psutil.net_io_counters()
    bytes_sent_new = net_io_new.bytes_sent
    bytes_recv_new = net_io_new.bytes_recv

    # 计算发送和接收速率（字节/秒）
    upload_speed_bps = bytes_sent_new - bytes_sent  # 字节/秒
    download_speed_bps = bytes_recv_new - bytes_recv

    speed_monitor.update_download_speed(download_speed_bps)

    # 格式化输出
    upload_speed = format_speed(upload_speed_bps)
    download_speed = format_speed(download_speed_bps)

    return f"network: ▲{upload_speed} ▼{download_speed}"


if __name__ == "__main__":
    pass
