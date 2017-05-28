# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from django_perf_rec import get_perf_path, get_record_name, record

from .utils import run_query


@pytest.fixture
def record_performance_build_name(request):
    record_name = get_record_name(
        class_name=request.cls.__name__ if request.cls is not None else None,
        test_name=request.function.__name__,
    )
    path = get_perf_path(file_path=request.fspath.strpath)
    with record(record_name=record_name, path=path):
        yield


@pytest.mark.django_db
def test_simple(record_performance_build_name):
    run_query('default', 'SELECT 1337')
