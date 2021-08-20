import errno
import os
from typing import Any, Dict, Optional

import yaml
from django.core.files import locks

from django_perf_rec.types import PerformanceRecord


class KVFile:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.data = self.load(file_name)

    def __len__(self) -> int:
        return len(self.data)

    LOAD_CACHE: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def load(cls, file_name: str) -> Dict[str, PerformanceRecord]:
        if file_name not in cls.LOAD_CACHE:
            cls.LOAD_CACHE[file_name] = cls.load_file(file_name)
        return cls.LOAD_CACHE[file_name]

    @classmethod
    def load_file(cls, file_name: str) -> Dict[str, PerformanceRecord]:
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
            raise TypeError(f"YAML content of {file_name} is not a dictionary")

        return data

    @classmethod
    def _clear_load_cache(cls) -> None:
        # Should really only be used in testing this class
        cls.LOAD_CACHE = {}

    def get(
        self, key: str, default: Optional[PerformanceRecord]
    ) -> Optional[PerformanceRecord]:
        return self.data.get(key, default)

    def set_and_save(self, key: str, value: PerformanceRecord) -> None:
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
