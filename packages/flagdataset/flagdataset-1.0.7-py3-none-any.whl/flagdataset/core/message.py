import datetime
import queue
import threading
import time

from ..utils.speed_monitor import network_speed
from ..utils.status import status_manager
from . import db

e_stop_watch = threading.Event()
q_message = queue.Queue(maxsize=1)

stop_message = ""


def watch_proc(proc=True):

    while True:
        stop = e_stop_watch.wait(timeout=1)
        if stop:
            break
        try:
            msg = q_message.get_nowait()
        except queue.Empty:
            msg = ""
        if proc:
            all_count = db.get_all_count()
            completed_count = db.get_completed_count()
            extra = f"<{completed_count} / {all_count}> "
        else:
            extra = ""

        if msg == "":
            continue

        msg_speed = network_speed()
        print(
            f"\r\033[2K{extra} {datetime.datetime.now()} {msg_speed} {status_manager}",
            end="",
        )

    time.sleep(1)
    msg_speed = network_speed()
    all_count = db.get_all_count()
    completed_count = db.get_completed_count()
    extra = f"<{completed_count} / {all_count}> "
    print(
        f"\r\033[2K{extra} {datetime.datetime.now()} {msg_speed} {status_manager}",
        end="",
    )
    print(f"\n{stop_message}")


def watch_stop():
    e_stop_watch.set()


def put(msg):
    if q_message.full():
        return
    q_message.put(f"{msg}")


def stop(msg):
    global stop_message
    stop_message = msg
