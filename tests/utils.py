import errno
import os
import shutil
from contextlib import contextmanager

from django.db import connections

from django_perf_rec import pytest_plugin


def run_query(alias, sql, params=None):
    with connections[alias].cursor() as cursor:
        cursor.execute(sql, params)


@contextmanager
def temporary_path(path):
    ensure_path_does_not_exist(path)
    yield
    ensure_path_does_not_exist(path)


def ensure_path_does_not_exist(path):
    if path.endswith('/'):
        shutil.rmtree(path, ignore_errors=True)
    else:
        try:
            os.unlink(path)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise


@contextmanager
def pretend_not_under_pytest():
    orig = pytest_plugin.in_pytest
    pytest_plugin.in_pytest = False
    try:
        yield
    finally:
        pytest_plugin.in_pytest = orig
