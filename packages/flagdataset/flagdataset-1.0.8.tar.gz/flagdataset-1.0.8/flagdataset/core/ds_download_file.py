import os
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

from ..config import settings
from ..utils.status import status_manager
from . import logger, login, message
from .spider import Spider


cpu_count = os.cpu_count() * 2 if os.cpu_count() < 16 else 32

download_worker_size = cpu_count * 100
download_worker_queue = Queue(maxsize=download_worker_size)

download_worker_pool = ThreadPoolExecutor(cpu_count)


def run_downloader(dataset_id, path, **kwargs):
    from ..storage import storage_api, storage_dataset, storage_wr

    ak, sk = login.load()  # noqa
    kwargs.setdefault("dataset", dataset_id)
    kwargs.setdefault("ak", ak)
    kwargs.setdefault("sk", sk)
    kwargs.setdefault("intranet", "public")
    kwargs.setdefault("host", "http://internal-data.baai.ac.cn")
    kwargs.setdefault("level", "INFO")
    kwargs.setdefault("path", path)

    config = settings.Application(**kwargs)

    print(f"{config}")
    logger.init()

    # 上报数据
    storage_dataset.update_download_num(status=0)

    p_watch = threading.Thread(target=message.watch_proc, args=(False,))
    p_watch.start()

    # 获取文件数据
    try:
        resp = storage_api.http_get_files(dataset_id, prefix=path)
    except Exception as e:
        print(e)
        return

    bucket = resp[1]
    prefix = resp[2]

    name = bucket + prefix.rstrip("/") + path

    dw_endpoint = storage_api.presigned_url(name)

    ok, size = storage_wr.read_meta(dw_endpoint)
    status_manager.required_add_size(size)

    spider = Spider(
        name,
        size,
        executor_poll=download_worker_pool,
        executor_pipeline=download_worker_queue,
    )
    spider.run()

    download_worker_pool.shutdown(wait=True)
    print("\n下载完毕")

    message.watch_stop()

    # 上报数据
    storage_dataset.update_download_num(status=1)
