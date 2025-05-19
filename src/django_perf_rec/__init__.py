from __future__ import annotations

try:
    import pytest

    _HAVE_PYTEST = True
except ImportError:
    _HAVE_PYTEST = False

if _HAVE_PYTEST:
    pytest.register_assert_rewrite("django_perf_rec.api")

from django_perf_rec.api import (
    TestCaseMixin,  # noqa: E402
    get_perf_path,
    get_record_name,
    record,
)

__all__ = [
    "TestCaseMixin",
    "get_record_name",
    "get_perf_path",
    "record",
]
