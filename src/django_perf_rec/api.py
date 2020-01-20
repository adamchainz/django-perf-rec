import os
from threading import local

from django.utils.functional import SimpleLazyObject

from django_perf_rec import pytest_plugin
from django_perf_rec.cache import AllCacheRecorder
from django_perf_rec.db import AllDBRecorder
from django_perf_rec.settings import perf_rec_settings
from django_perf_rec.utils import current_test, record_diff
from django_perf_rec.yaml import KVFile

record_current = local()


def record(*, record_name=None, path=None):
    # Lazy since we may not need this to determine record_name or path,
    # depending on logic below
    test_details = SimpleLazyObject(current_test)

    if path is None or path.endswith("/"):
        file_name = get_perf_path(test_details.file_path)
    else:
        file_name = path

    if path is not None and path.endswith("/"):
        if not os.path.isabs(path):
            directory = os.path.join(os.path.dirname(test_details.file_path), path)
            if not os.path.exists(directory):
                os.makedirs(directory)
        else:
            directory = path

        file_name = os.path.join(directory, os.path.basename(file_name))

    if record_name is None:
        record_name = get_record_name(
            test_name=test_details.test_name,
            class_name=test_details.class_name,
            file_name=file_name,
        )

    return PerformanceRecorder(file_name, record_name)


def get_perf_path(file_path):
    if file_path.endswith(".py"):
        perf_path = file_path[: -len(".py")] + ".perf.yml"
    elif file_path.endswith(".pyc"):
        perf_path = file_path[: -len(".pyc")] + ".perf.yml"
    else:
        perf_path = file_path + ".perf.yml"
    return perf_path


def get_record_name(test_name, class_name=None, file_name=""):
    if class_name:
        record_name = "{class_}.{test}".format(class_=class_name, test=test_name)
    else:
        record_name = test_name

    # Multiple calls inside the same test should end up suffixing with .2, .3 etc.
    record_spec = (file_name, record_name)
    if getattr(record_current, "record_spec", None) == record_spec:
        record_current.counter += 1
        record_name = record_name + ".{}".format(record_current.counter)
    else:
        record_current.record_spec = record_spec
        record_current.counter = 1

    return record_name


class PerformanceRecorder:
    def __init__(self, file_name, record_name):
        self.file_name = file_name
        self.record_name = record_name

        self.record = []
        self.db_recorder = AllDBRecorder(self.on_op)
        self.cache_recorder = AllCacheRecorder(self.on_op)

    def __enter__(self):
        self.db_recorder.__enter__()
        self.cache_recorder.__enter__()
        self.load_recordings()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.cache_recorder.__exit__(exc_type, exc_value, exc_traceback)
        self.db_recorder.__exit__(exc_type, exc_value, exc_traceback)

        if exc_type is None:
            self.save_or_assert()

    def on_op(self, op):
        self.record.append({op.name: op.query})

    def load_recordings(self):
        self.records_file = KVFile(self.file_name)

    def save_or_assert(self):
        orig_record = self.records_file.get(self.record_name, None)

        if perf_rec_settings.MODE == "none":
            assert (
                orig_record is not None
            ), "Original performance record does not exist for {}".format(
                self.record_name
            )

        if orig_record is not None:
            msg = "Performance record did not match for {}".format(self.record_name)
            if not pytest_plugin.in_pytest:
                msg += "\n{}".format(record_diff(orig_record, self.record))
            assert self.record == orig_record, msg

        self.records_file.set_and_save(self.record_name, self.record)

        if perf_rec_settings.MODE == "all":
            assert (
                orig_record is not None
            ), "Original performance record did not exist for {}".format(
                self.record_name
            )


class TestCaseMixin:
    """
    Adds record_performance() method to TestCase class it's mixed into
    for easy import-free use.
    """

    def record_performance(self, *, record_name=None, path=None):
        return record(record_name=record_name, path=path)
