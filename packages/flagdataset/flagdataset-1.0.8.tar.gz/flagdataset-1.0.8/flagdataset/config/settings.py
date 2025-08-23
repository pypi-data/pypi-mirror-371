import os


user_path = os.path.expanduser("~")

default_token_path = os.path.join(user_path, ".sdk_download/token.json")
default_spider_path = os.path.join(user_path, ".sdk_download/tmp")
default_download_path = os.path.join(user_path, ".sdk_download/download")

default_logger_file = os.path.join(user_path, ".sdk_download/download.log")
default_logger_format = "{time:HH:mm:ss} {level} {thread.name} {message}"


def singleton(cls):
    _instance = {}
    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


class Application:
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance  # noqa

    def __init__(self, ak=None, sk=None, **kwargs):
        """
        internet: public, private
        """

        if not self._initialized:

            self.ak = ak
            self.sk = sk

            self.intranet = kwargs.get("intranet", "public")  # public, private
            self.dataset = kwargs.get("dataset", None)
            self.target = kwargs.get("target") or default_download_path  # save path
            self.path = kwargs.get("path")

            self.debug = kwargs.get("debug", False)
            self.level = kwargs.get("level", "INFO")
            self.host = kwargs.get("host") or "http://120.92.210.10"

            self.api_endpoint = f"{self.host}/api/datastorage/api/v5"  # 不能加 /
            self.auth_endpoint = f"{self.host}/api/user-srv"
            self.report_endpoint = f"{self.host}/api/dataset"
            self.temp_path = kwargs.get("temp_path") or default_spider_path

            self._initialized = True

    def __str__(self):
        target = self.target if self.target else "-"

        return (
            f"config: <{id(self)}-{self.intranet}>, "
            f"ak: {self.ak}, "
            f"host: {self.host}, "
            f"path: {self.path}, "
            f"target: {target}\n"
            f"temp_path: {self.temp_path}"
        )
