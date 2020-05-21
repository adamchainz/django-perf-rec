import errno
import os

import yaml
from django.core.files import locks


class KVFile:
    def __init__(self, file_name):
        self.file_name = file_name
        self.data = self.load(file_name)

    def __len__(self):
        return len(self.data)

    LOAD_CACHE = {}

    @classmethod
    def load(cls, file_name):
        if file_name not in cls.LOAD_CACHE:
            cls.LOAD_CACHE[file_name] = cls.load_file(file_name)
        return cls.LOAD_CACHE[file_name]

    @classmethod
    def load_file(cls, file_name):
        try:
            with open(file_name) as fp:
                locks.lock(fp, locks.LOCK_EX)
                content = fp.read()
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                content = "{}"
            else:
                raise

        data = yaml.safe_load(content)

        if data is None:
            return {}
        elif not isinstance(data, dict):
            raise TypeError("YAML content of {} is not a dictionary".format(file_name))

        return data

    @classmethod
    def _clear_load_cache(cls):
        # Should really only be used in testing this class
        cls.LOAD_CACHE = {}

    def get(self, key, default):
        return self.data.get(key, default)

    def set_and_save(self, key, value):
        if self.data.get(key, object()) == value:
            return

        fd = os.open(self.file_name, os.O_RDWR | os.O_CREAT, mode=0o666)
        with os.fdopen(fd, "r+") as fp:
            locks.lock(fd, locks.LOCK_EX)

            data = yaml.safe_load(fp)
            if data is None:
                data = {}

            self.data[key] = value
            data[key] = value

            fp.seek(0)
            yaml.safe_dump(
                data, fp, default_flow_style=False, allow_unicode=True, width=10000
            )
