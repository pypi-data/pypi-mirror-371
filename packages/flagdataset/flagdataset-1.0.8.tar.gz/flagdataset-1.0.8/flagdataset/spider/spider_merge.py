import hashlib
import mmap
import pathlib
import shutil

from loguru import logger

from ..config import settings


def range_index(file_size, part_size=1024 * 1024 * 5):
    idx = []
    for i, _ in enumerate(range(0, file_size, part_size)):
        idx.append(i)
    return idx


def check_part(name, file_size, part_size=1024 * 1024 * 5, target=None):

    conf = settings.Application()

    target_dir = pathlib.Path(target)

    path_target = name.split("://")[1].split("/", maxsplit=1)  # noqa

    target_path = target_dir / pathlib.Path(path_target[1])
    target_path.parent.mkdir(parents=True, exist_ok=True)

    hex_digest = hashlib.sha256(name.encode("utf-8")).hexdigest()

    tmp_path = pathlib.Path(conf.temp_path) / hex_digest

    tmp_list = list(tmp_path.glob("*.tmp"))
    tmp_list.sort()

    tmp_files = sorted(tmp_list, key=lambda x: int(x.name.split("_")[0]))

    # 检查分片是否正确
    tmp_index = set(map(lambda x: int(x.name.split("_")[0]), tmp_files))
    range_idx = set(range_index(file_size, part_size))

    # want_idx = range_idx - tmp_index

    return tmp_index, range_idx


def merge_part(name, file_size, part_size=1024 * 1024 * 5, target=None) -> int:

    conf = settings.Application()  # noqa

    target_dir = pathlib.Path(target)

    path_target = name.split("://")[1].split("/", maxsplit=1)

    target_path = target_dir / pathlib.Path(path_target[1])
    target_path.parent.mkdir(parents=True, exist_ok=True)

    hex_digest = hashlib.sha256(name.encode("utf-8")).hexdigest()

    tmp_path = pathlib.Path(conf.temp_path) / hex_digest

    tmp_list = list(tmp_path.glob("*.tmp"))
    tmp_list.sort()

    tmp_files = sorted(tmp_list, key=lambda x: int(x.name.split("_")[0]))

    # 检查分片是否正确
    tmp_index = set(map(lambda x: int(x.name.split("_")[0]), tmp_files))
    range_idx = set(range_index(file_size, part_size))

    want_idx = range_idx - tmp_index
    if want_idx:
        logger.warning(f"分片 {want_idx} 丢失: {tmp_path}")

    # TODO: 处理丢失分片，目前缺少时不合并
    if want_idx:
        return -1

    total_size = 0
    with target_path.open("ab") as target_writer:
        for tmp_file in tmp_files:
            with tmp_file.open("rb") as f:
                with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
                    target_writer.write(mm)
                    total_size += mm.size()

    try:
        shutil.rmtree(tmp_path)
    except Exception as e:
        logger.error(e)

    return total_size
