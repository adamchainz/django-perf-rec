from __future__ import annotations

import errno
import os
import shutil
import traceback
from collections.abc import Generator
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, TypeVar, cast
from unittest import mock

from django.db import connections

from django_perf_rec import pytest_plugin


def run_query(alias: str, sql: str, params: list[str] | None = None) -> None:
    with connections[alias].cursor() as cursor:
        cursor.execute(sql, params)


@contextmanager
def temporary_path(path: str) -> Generator[None]:
    ensure_path_does_not_exist(path)
    yield
    ensure_path_does_not_exist(path)


def ensure_path_does_not_exist(path: str) -> None:
    if path.endswith("/"):
        shutil.rmtree(path, ignore_errors=True)
    else:
        try:
            os.unlink(path)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise


@contextmanager
def pretend_not_under_pytest() -> Generator[None]:
    orig = pytest_plugin.in_pytest
    pytest_plugin.in_pytest = False
    try:
        yield
    finally:
        pytest_plugin.in_pytest = orig


TestFunc = TypeVar("TestFunc", bound=Callable[..., None])


def override_extract_stack(func: TestFunc) -> TestFunc:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        summary = traceback.extract_stack()
        with mock.patch.object(traceback, "extract_stack", return_value=summary):
            func(*args, stack_summary=summary, **kwargs)

    return cast(TestFunc, wrapper)
