import pytest
from django.core.cache import caches
from django.test import SimpleTestCase, TestCase, override_settings

from django_perf_rec.cache import AllCacheRecorder, CacheOp, CacheRecorder

try:
    from unittest import mock
except ImportError:
    import mock


class CacheOpTests(SimpleTestCase):
    def test_clean_key_integer(self):
        assert CacheOp.clean_key("foo1") == "foo#"

    def test_clean_key_uuid(self):
        assert CacheOp.clean_key("bdfc9986-d461-4a5e-bf98-8688993abcfb") == "#"

    def test_clean_key_random_hash(self):
        assert CacheOp.clean_key("abc123abc123abc123abc123abc12345") == "#"

    def test_clean_key_session_key_cache_backend(self):
        key = "django.contrib.sessions.cacheabcdefghijklmnopqrstuvwxyz012345"
        assert CacheOp.clean_key(key) == "django.contrib.sessions.cache#"

    def test_clean_key_session_key_cached_db_backend(self):
        key = "django.contrib.sessions.cached_db" + "abcdefghijklmnopqrstuvwxyz012345"
        assert CacheOp.clean_key(key) == "django.contrib.sessions.cached_db#"

    def test_key(self):
        op = CacheOp("default", "foo", "bar")
        assert op.alias == "default"
        assert op.operation == "foo"
        assert op.key_or_keys == "bar"

    def test_keys(self):
        op = CacheOp("default", "foo", ["bar", "baz"])
        assert op.alias == "default"
        assert op.operation == "foo"
        assert op.key_or_keys == ["bar", "baz"]

    def test_invalid(self):
        with pytest.raises(ValueError):
            CacheOp("x", "foo", object())

    def test_equal(self):
        assert CacheOp("x", "foo", "bar") == CacheOp("x", "foo", "bar")

    def test_equal_with_traceback(self):
        assert CacheOp("x", "foo", "bar", "traceback") == CacheOp(
            "x", "foo", "bar", "traceback"
        )

    def test_not_equal_alias(self):
        assert CacheOp("x", "foo", "bar") != CacheOp("y", "foo", "bar")

    def test_not_equal_operation(self):
        assert CacheOp("x", "foo", "bar") != CacheOp("x", "bar", "bar")

    def test_not_equal_keys(self):
        assert CacheOp("x", "foo", ["bar"]) != CacheOp("x", "foo", ["baz"])

    def test_not_equal_traceback(self):
        assert CacheOp("x", "foo", "bar", "traceback") != CacheOp("x", "foo", "bar")


class CacheRecorderTests(TestCase):
    def test_default(self):
        callback = mock.Mock()
        with CacheRecorder("default", callback):
            caches["default"].get("foo")
        callback.assert_called_once_with(CacheOp("default", "get", "foo"))

    def test_secondary(self):
        callback = mock.Mock()
        with CacheRecorder("second", callback):
            caches["second"].get("foo")
        callback.assert_called_once_with(CacheOp("second", "get", "foo"))

    def test_secondary_default_not_recorded(self):
        callback = mock.Mock()
        with CacheRecorder("second", callback):
            caches["default"].get("foo")
        assert len(callback.mock_calls) == 0

    @override_settings(PERF_REC={"TRACE_CACHE_PATTERN": "foo"})
    def test_record_traceback(self):
        callback = mock.Mock()
        with CacheRecorder("default", callback):
            caches["default"].get("foo")
            caches["default"].get("bar")

        assert len(callback.mock_calls) == 2
        assert "/django-perf-rec/django_perf_rec/cache.py" in str(
            callback.call_args_list[0][0][0].tb
        )
        assert callback.call_args_list[1][0][0].tb is None


class AllCacheRecorderTests(TestCase):
    def test_records_all(self):
        callback = mock.Mock()
        with AllCacheRecorder(callback):
            caches["default"].get("foo")
            caches["second"].set("bar", "baz")
            caches["default"].delete_many(["foo"])

        assert callback.mock_calls == [
            mock.call(CacheOp("default", "get", "foo")),
            mock.call(CacheOp("second", "set", "bar")),
            mock.call(CacheOp("default", "delete_many", ["foo"])),
        ]
