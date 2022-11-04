from __future__ import annotations

import os
from functools import lru_cache
from threading import local
from types import TracebackType
from typing import Callable

from django_perf_rec import pytest_plugin
from django_perf_rec.cache import AllCacheRecorder
from django_perf_rec.db import AllDBRecorder
from django_perf_rec.operation import Operation
from django_perf_rec.settings import perf_rec_settings
from django_perf_rec.types import PerformanceRecordItem
from django_perf_rec.utils import current_test
from django_perf_rec.utils import record_diff
from django_perf_rec.utils import TestDetails
from django_perf_rec.yaml import KVFile


def get_perf_path(file_path: str) -> str:
    if file_path.endswith(".py"):
        perf_path = file_path[: -len(".py")] + ".perf.yml"
    elif file_path.endswith(".pyc"):
        perf_path = file_path[: -len(".pyc")] + ".perf.yml"
    else:
        perf_path = file_path + ".perf.yml"
    return perf_path


record_current = local()


def get_record_name(
    test_name: str,
    class_name: str | None = None,
    file_name: str = "",
) -> str:
    if class_name:
        record_name = f"{class_name}.{test_name}"
    else:
        record_name = test_name

    # Multiple calls inside the same test should end up suffixing with .2, .3 etc.
    record_spec = (file_name, record_name)
    if getattr(record_current, "record_spec", None) == record_spec:
        record_current.counter += 1
        record_name = record_name + f".{record_current.counter}"
    else:
        record_current.record_spec = record_spec
        record_current.counter = 1

    return record_name


class PerformanceRecorder:
    def __init__(
        self,
        file_name: str,
        record_name: str,
        capture_traceback: Callable[[Operation], bool] | None,
        capture_operation: Callable[[Operation], bool] | None,
    ) -> None:
        self.file_name = file_name
        self.record_name = record_name

        self.record: list[PerformanceRecordItem] = []
        self.db_recorder = AllDBRecorder(self.on_op)
        self.cache_recorder = AllCacheRecorder(self.on_op)
        self.capture_operation = capture_operation
        self.capture_traceback = capture_traceback

    def __enter__(self) -> None:
        self.db_recorder.__enter__()
        self.cache_recorder.__enter__()
        self.load_recordings()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> None:
        self.cache_recorder.__exit__(exc_type, exc_value, exc_traceback)
        self.db_recorder.__exit__(exc_type, exc_value, exc_traceback)

        if exc_type is None:
            self.save_or_assert()

    def on_op(self, op: Operation) -> None:
        record = {op.name: op.query}

        if self.capture_operation and not self.capture_operation(op):
            return

        if self.capture_traceback and self.capture_traceback(op):
            record["traceback"] = op.traceback.format()

        self.record.append(record)

    def load_recordings(self) -> None:
        self.records_file = KVFile(self.file_name)

    def save_or_assert(self) -> None:
        orig_record = self.records_file.get(self.record_name, None)
        if perf_rec_settings.MODE == "none":
            assert (
                orig_record is not None
            ), "Original performance record does not exist for {}".format(
                self.record_name
            )

        if orig_record is not None and perf_rec_settings.MODE != "overwrite":
            msg = f"Performance record did not match for {self.record_name}"
            if not pytest_plugin.in_pytest:
                msg += f"\n{record_diff(orig_record, self.record)}"
            assert self.record == orig_record, msg

        self.records_file.set_and_save(self.record_name, self.record)

        if perf_rec_settings.MODE == "all":
            assert (
                orig_record is not None
            ), "Original performance record did not exist for {}".format(
                self.record_name
            )


def record(
    *,
    record_name: str | None = None,
    path: str | None = None,
    capture_traceback: Callable[[Operation], bool] | None = None,
    capture_operation: Callable[[Operation], bool] | None = None,
) -> PerformanceRecorder:
    @lru_cache(maxsize=None)
    def get_test_details() -> TestDetails:
        return current_test()

    if path is None or path.endswith("/"):
        file_name = get_perf_path(get_test_details().file_path)
    else:
        file_name = path

    if path is not None and path.endswith("/"):
        if not os.path.isabs(path):
            directory = os.path.join(
                os.path.dirname(get_test_details().file_path), path
            )
            if not os.path.exists(directory):
                os.makedirs(directory)
        else:
            directory = path

        file_name = os.path.join(directory, os.path.basename(file_name))

    if record_name is None:
        record_name = get_record_name(
            test_name=get_test_details().test_name,
            class_name=get_test_details().class_name,
            file_name=file_name,
        )

    return PerformanceRecorder(
        file_name,
        record_name,
        capture_traceback,
        capture_operation,
    )


class TestCaseMixin:
    """
    Adds record_performance() method to TestCase class it's mixed into
    for easy import-free use.
    """

    def record_performance(
        self, *, record_name: str | None = None, path: str | None = None
    ) -> PerformanceRecorder:
        return record(record_name=record_name, path=path)
