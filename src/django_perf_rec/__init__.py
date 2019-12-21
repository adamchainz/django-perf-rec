"""
isort:skip_file
"""
try:
    import pytest
except ImportError:
    pytest = None

if pytest is not None:
    pytest.register_assert_rewrite("django_perf_rec.api")

from django_perf_rec.api import (
    TestCaseMixin,
    get_record_name,
    get_perf_path,
    record,
)  # noqa: E402

__all__ = [
    "TestCaseMixin",
    "get_record_name",
    "get_perf_path",
    "record",
]
