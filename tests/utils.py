# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import errno
import os
import shutil
from contextlib import contextmanager

from django.db import connections


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
