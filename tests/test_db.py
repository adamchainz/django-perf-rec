# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import mock
from django.test import SimpleTestCase, TestCase

from django_perf_rec.db import AllDBRecorder, DBOp, DBRecorder

from .utils import run_query


class DBOpTests(SimpleTestCase):

    def test_create(self):
        op = DBOp('myalias', 'SELECT 1')
        assert op.alias == 'myalias'
        assert op.sql == 'SELECT 1'

    def test_equal(self):
        assert (
            DBOp('foo', 'bar') ==
            DBOp('foo', 'bar')
        )

    def test_not_equal_alias(self):
        assert (
            DBOp('foo', 'bar') !=
            DBOp('baz', 'bar')
        )

    def test_not_equal_sql(self):
        assert (
            DBOp('foo', 'bar') !=
            DBOp('foo', 'baz')
        )


class DBRecorderTests(TestCase):

    def test_default(self):
        callback = mock.Mock()
        with DBRecorder('default', callback):
            run_query('default', 'SELECT 1')
        callback.assert_called_once_with(
            DBOp('default', 'SELECT #')
        )

    def test_secondary(self):
        callback = mock.Mock()
        with DBRecorder('second', callback):
            run_query('second', 'SELECT 1')
        callback.assert_called_once_with(
            DBOp('second', 'SELECT #')
        )

    def test_replica(self):
        callback = mock.Mock()
        with DBRecorder('replica', callback):
            run_query('replica', 'SELECT 1')
        callback.assert_called_once_with(
            DBOp('replica', 'SELECT #')
        )

    def test_secondary_default_not_recorded(self):
        callback = mock.Mock()
        with DBRecorder('second', callback):
            run_query('default', 'SELECT 1')
        assert len(callback.mock_calls) == 0


class AllDBRecorderTests(TestCase):

    def test_records_all(self):
        callback = mock.Mock()
        with AllDBRecorder(callback):
            run_query('replica', 'SELECT 1')
            run_query('default', 'SELECT 2')
            run_query('second', 'SELECT 3')

        assert callback.mock_calls == [
            mock.call(DBOp('replica', 'SELECT #')),
            mock.call(DBOp('default', 'SELECT #')),
            mock.call(DBOp('second', 'SELECT #')),
        ]
