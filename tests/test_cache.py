from __future__ import annotations

from traceback import extract_stack
from unittest import mock

import pytest
from django.core.cache import caches
from django.test import SimpleTestCase
from django.test import TestCase

from django_perf_rec.cache import AllCacheRecorder
from django_perf_rec.cache import CacheOp
from django_perf_rec.cache import CacheRecorder
from tests.utils import override_extract_stack


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
        summary = extract_stack()
        op = CacheOp("default", "foo", "bar", summary)
        assert op.alias == "default"
        assert op.operation == "foo"
        assert op.query == "bar"
        assert op.traceback == summary

    def test_keys(self):
        op = CacheOp("default", "foo", ["bar", "baz"], extract_stack())
        assert op.alias == "default"
        assert op.operation == "foo"
        assert op.query == ["bar", "baz"]

    def test_keys_frozenset(self):
        op = CacheOp("default", "foo", frozenset(["bar", "baz"]), extract_stack())
        assert op.alias == "default"
        assert op.operation == "foo"
        assert op.query == ["bar", "baz"]

    def test_keys_dict_keys(self):
        op = CacheOp("default", "foo", {"bar": "baz"}.keys(), extract_stack())
        assert op.alias == "default"
        assert op.operation == "foo"
        assert op.query == ["bar"]

    def test_invalid(self):
        with pytest.raises(ValueError):
            CacheOp("x", "foo", object(), extract_stack())  # type: ignore [arg-type]

    def test_equal(self):
        summary = extract_stack()
        assert CacheOp("x", "foo", "bar", summary) == CacheOp(
            "x", "foo", "bar", summary
        )

    def test_not_equal_alias(self):
        summary = extract_stack()
        assert CacheOp("x", "foo", "bar", summary) != CacheOp(
            "y", "foo", "bar", summary
        )

    def test_not_equal_operation(self):
        summary = extract_stack()
        assert CacheOp("x", "foo", "bar", summary) != CacheOp(
            "x", "bar", "bar", summary
        )

    def test_not_equal_keys(self):
        summary = extract_stack()
        assert CacheOp("x", "foo", ["bar"], summary) != CacheOp(
            "x", "foo", ["baz"], summary
        )

    def test_not_equal_traceback(self):
        assert CacheOp("x", "foo", "bar", extract_stack(limit=1)) != CacheOp(
            "x", "foo", "bar", extract_stack(limit=2)
        )


class CacheRecorderTests(TestCase):
    @override_extract_stack
    def test_default(self, stack_summary):
        callback = mock.Mock()
        with CacheRecorder("default", callback):
            caches["default"].get("foo")
        callback.assert_called_once_with(
            CacheOp("default", "get", "foo", stack_summary)
        )

    @override_extract_stack
    def test_secondary(self, stack_summary):
        callback = mock.Mock()
        with CacheRecorder("second", callback):
            caches["second"].get("foo")
        callback.assert_called_once_with(CacheOp("second", "get", "foo", stack_summary))

    def test_secondary_default_not_recorded(self):
        callback = mock.Mock()
        with CacheRecorder("second", callback):
            caches["default"].get("foo")
        assert len(callback.mock_calls) == 0

    def test_record_traceback(self):
        callback = mock.Mock()
        with CacheRecorder("default", callback):
            caches["default"].get("foo")

        assert len(callback.mock_calls) == 1
        assert "django_perf_rec/cache.py" in str(
            callback.call_args_list[0][0][0].traceback
        )


class AllCacheRecorderTests(TestCase):
    @override_extract_stack
    def test_records_all(self, stack_summary):
        callback = mock.Mock()
        with AllCacheRecorder(callback):
            caches["default"].get("foo")
            caches["second"].set("bar", "baz")
            caches["default"].delete_many(["foo"])

        assert callback.mock_calls == [
            mock.call(CacheOp("default", "get", "foo", stack_summary)),
            mock.call(CacheOp("second", "set", "bar", stack_summary)),
            mock.call(CacheOp("default", "delete_many", ["foo"], stack_summary)),
        ]
