from __future__ import annotations

from traceback import extract_stack
from traceback import StackSummary
from unittest import mock

from django.test import SimpleTestCase
from django.test import TestCase

from django_perf_rec.db import AllDBRecorder
from django_perf_rec.db import DBOp
from django_perf_rec.db import DBRecorder
from tests.utils import override_extract_stack
from tests.utils import run_query


class DBOpTests(SimpleTestCase):
    def test_create(self):
        op = DBOp("myalias", "SELECT 1", extract_stack())
        assert op.alias == "myalias"
        assert op.query == "SELECT 1"
        assert isinstance(op.traceback, StackSummary)

    def test_equal(self):
        summary = extract_stack()
        assert DBOp("foo", "bar", summary) == DBOp("foo", "bar", summary)

    def test_not_equal_alias(self):
        summary = extract_stack()
        assert DBOp("foo", "bar", summary) != DBOp("baz", "bar", summary)

    def test_not_equal_sql(self):
        summary = extract_stack()
        assert DBOp("foo", "bar", summary) != DBOp("foo", "baz", summary)

    def test_not_equal_traceback(self):
        assert DBOp("foo", "bar", extract_stack(limit=1)) != DBOp(
            "foo", "bar", extract_stack(limit=2)
        )


class DBRecorderTests(TestCase):
    databases = {"default", "second", "replica"}

    @override_extract_stack
    def test_default(self, stack_summary):
        callback = mock.Mock()
        with DBRecorder("default", callback):
            run_query("default", "SELECT 1")
        callback.assert_called_once_with(DBOp("default", "SELECT #", stack_summary))

    @override_extract_stack
    def test_secondary(self, stack_summary):
        callback = mock.Mock()
        with DBRecorder("second", callback):
            run_query("second", "SELECT 1")
        callback.assert_called_once_with(DBOp("second", "SELECT #", stack_summary))

    @override_extract_stack
    def test_replica(self, stack_summary):
        callback = mock.Mock()
        with DBRecorder("replica", callback):
            run_query("replica", "SELECT 1")
        callback.assert_called_once_with(DBOp("replica", "SELECT #", stack_summary))

    def test_secondary_default_not_recorded(self):
        callback = mock.Mock()
        with DBRecorder("second", callback):
            run_query("default", "SELECT 1")
        assert len(callback.mock_calls) == 0

    def test_record_traceback(self):
        callback = mock.Mock()
        with DBRecorder("default", callback):
            run_query("default", "SELECT 1")

        assert len(callback.mock_calls) == 1
        assert "django_perf_rec/db.py" in str(
            callback.call_args_list[0][0][0].traceback
        )


class AllDBRecorderTests(TestCase):
    databases = {"default", "second", "replica"}

    @override_extract_stack
    def test_records_all(self, stack_summary):
        callback = mock.Mock()
        with AllDBRecorder(callback):
            run_query("replica", "SELECT 1")
            run_query("default", "SELECT 2")
            run_query("second", "SELECT 3")

        assert callback.mock_calls == [
            mock.call(DBOp("replica", "SELECT #", stack_summary)),
            mock.call(DBOp("default", "SELECT #", stack_summary)),
            mock.call(DBOp("second", "SELECT #", stack_summary)),
        ]
