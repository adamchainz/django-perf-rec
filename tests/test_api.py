# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import errno
import os

import pytest
import six
from django.core.cache import caches
from django.test import TestCase

from django_performance_recorder import record


class RecordTests(TestCase):

    def test_single_cache_op(self):
        with record():
            caches['default'].get('foo')

    def test_multiple_cache_ops(self):
        with record():
            caches['default'].set('foo', 'bar')
            caches['second'].get_many(['foo', 'bar'])
            caches['default'].delete('foo')

    def test_multiple_calls_in_same_function_are_different_records(self):
        with record():
            caches['default'].get('foo')

        with record():
            caches['default'].get('bar')

    def test_custom_name(self):
        with record(record_name='custom'):
            caches['default'].get('foo')

    def test_custom_name_multiple_calls(self):
        with record(record_name='custom'):
            caches['default'].get('foo')

        with pytest.raises(AssertionError) as excinfo:
            with record(record_name='custom'):
                caches['default'].get('bar')

        assert 'Performance record did not match' in six.text_type(excinfo.value)


class RecordBlankFileTests(TestCase):

    perf_name = __file__.replace('.py', '.empty.perf.yml')

    @classmethod
    def setUpClass(cls):
        super(RecordBlankFileTests, cls).setUpClass()
        cls.ensure_no_file()

    @classmethod
    def tearDownClass(cls):
        cls.ensure_no_file()
        super(RecordBlankFileTests, cls).tearDownClass()

    @classmethod
    def ensure_no_file(cls):
        try:
            os.unlink(cls.perf_name)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise

    def test_one(self):
        with record(file_name=self.perf_name):
            caches['default'].get('foo')

    def test_two(self):
        with record(file_name=self.perf_name):
            caches['default'].get('foo')
        with record(file_name=self.perf_name):
            caches['default'].get('foo')
