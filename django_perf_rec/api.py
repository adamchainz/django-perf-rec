# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
from threading import local

from django.core.cache import DEFAULT_CACHE_ALIAS
from django.db import DEFAULT_DB_ALIAS

from . import pytest_plugin
from .cache import AllCacheRecorder
from .db import AllDBRecorder
from .functional import kwargs_only
from .settings import perf_rec_settings
from .utils import current_test, record_diff

from .yaml import KVFile


record_current = local()


@kwargs_only
def record(record_name=None, path=None):
    test_details = current_test()

    if path is None or path.endswith('/'):
        file_name = test_details.file_path
        if file_name.endswith('.py'):
            file_name = file_name[:-len('.py')] + '.perf.yml'
        elif file_name.endswith('.pyc'):
            file_name = file_name[:-len('.pyc')] + '.perf.yml'
        else:
            file_name += '.perf.yml'
    else:
        file_name = path

    if path is not None and path.endswith('/'):
        directory = os.path.join(os.path.dirname(test_details.file_path), path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_name = os.path.join(directory, os.path.basename(file_name))

    if record_name is None:
        if test_details.class_name:
            record_name = '{class_}.{test}'.format(
                class_=test_details.class_name,
                test=test_details.test_name,
            )
        else:
            record_name = test_details.test_name

        # Multiple calls inside the same test should end up suffixing with .2, .3 etc.
        if getattr(record_current, 'record_name', None) == record_name:
            record_current.counter += 1
            record_name = record_name + '.{}'.format(record_current.counter)
        else:
            record_current.record_name = record_name
            record_current.counter = 1

    return PerformanceRecorder(file_name, record_name)


class PerformanceRecorder(object):

    def __init__(self, file_name, record_name):
        self.file_name = file_name
        self.record_name = record_name

        self.record = []
        self.db_recorder = AllDBRecorder(self.on_db_op)
        self.cache_recorder = AllCacheRecorder(self.on_cache_op)

    def __enter__(self):
        self.db_recorder.__enter__()
        self.cache_recorder.__enter__()
        self.load_recordings()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.cache_recorder.__exit__(exc_type, exc_value, exc_traceback)
        self.db_recorder.__exit__(exc_type, exc_value, exc_traceback)

        if exc_type is None:
            self.save_or_assert()

    def on_db_op(self, db_op):
        name_parts = ['db']
        if db_op.alias != DEFAULT_DB_ALIAS:
            name_parts.append(db_op.alias)
        name = '|'.join(name_parts)

        self.record.append({name: db_op.sql})

    def on_cache_op(self, cache_op):
        name_parts = ['cache']
        if cache_op.alias != DEFAULT_CACHE_ALIAS:
            name_parts.append(cache_op.alias)
        name_parts.append(cache_op.operation)
        name = '|'.join(name_parts)

        self.record.append({name: cache_op.key_or_keys})

    def load_recordings(self):
        self.records_file = KVFile(self.file_name)

    def save_or_assert(self):
        orig_record = self.records_file.get(self.record_name, None)

        if perf_rec_settings.MODE == 'none':
            assert orig_record is not None, "Original performance record does not exist for {}".format(self.record_name)

        if orig_record is not None:
            msg = "Performance record did not match for {}".format(
                self.record_name
            )
            if not pytest_plugin.in_pytest:
                msg += '\n{}'.format(
                    record_diff(orig_record, self.record)
                )
            assert self.record == orig_record, msg

        self.records_file.set_and_save(self.record_name, self.record)

        if perf_rec_settings.MODE == 'all':
            assert orig_record is not None, "Original performance record did not exist for {}".format(self.record_name)


class TestCaseMixin(object):
    """
    Adds record_performance() method to TestCase class it's mixed into
    for easy import-free use.
    """
    @kwargs_only
    def record_performance(self, record_name=None, path=None):
        return record(record_name=record_name, path=path)
