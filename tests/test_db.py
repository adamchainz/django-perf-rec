from unittest import mock

from django.test import SimpleTestCase, TestCase

from django_perf_rec.db import AllDBRecorder, DBOp, DBRecorder
from tests.utils import disable_traceback, run_query


class DBOpTests(SimpleTestCase):
    def test_create(self):
        op = DBOp("myalias", "SELECT 1", None)
        assert op.alias == "myalias"
        assert op.query == "SELECT 1"
        assert op.traceback is None

    def test_equal(self):
        assert DBOp("foo", "bar", "traceback") == DBOp("foo", "bar", "traceback")

    def test_not_equal_alias(self):
        assert DBOp("foo", "bar", None) != DBOp("baz", "bar", None)

    def test_not_equal_sql(self):
        assert DBOp("foo", "bar", None) != DBOp("foo", "baz", None)

    def test_not_equal_traceback(self):
        assert DBOp("foo", "bar", "traceback") != DBOp("foo", "baz", None)


class DBRecorderTests(TestCase):
    databases = ("default", "second", "replica")

    @disable_traceback
    def test_default(self, extract_stack):
        callback = mock.Mock()
        with DBRecorder("default", callback):
            run_query("default", "SELECT 1")
        callback.assert_called_once_with(DBOp("default", "SELECT #", None))

    @disable_traceback
    def test_secondary(self, extract_stack):
        callback = mock.Mock()
        with DBRecorder("second", callback):
            run_query("second", "SELECT 1")
        callback.assert_called_once_with(DBOp("second", "SELECT #", None))

    @disable_traceback
    def test_replica(self, extract_stack):
        callback = mock.Mock()
        with DBRecorder("replica", callback):
            run_query("replica", "SELECT 1")
        callback.assert_called_once_with(DBOp("replica", "SELECT #", None))

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
    databases = ("default", "second", "replica")

    @disable_traceback
    def test_records_all(self, extract_stack):
        callback = mock.Mock()
        with AllDBRecorder(callback):
            run_query("replica", "SELECT 1")
            run_query("default", "SELECT 2")
            run_query("second", "SELECT 3")

        assert callback.mock_calls == [
            mock.call(DBOp("replica", "SELECT #", None)),
            mock.call(DBOp("default", "SELECT #", None)),
            mock.call(DBOp("second", "SELECT #", None)),
        ]
