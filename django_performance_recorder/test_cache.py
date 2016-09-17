# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
from django_performance_recorder.cache import CacheOperation


def test_clean_key_integer():
    assert CacheOperation.clean_key('foo1') == 'foo#'


def test_clean_key_uuid():
    assert CacheOperation.clean_key('bdfc9986-d461-4a5e-bf98-8688993abcfb') == '#'


def test_clean_key_random_hash():
    assert CacheOperation.clean_key('abc123abc123abc123abc123abc12345') == '#'


def test_CacheOperation_key():
    op = CacheOperation('foo', 'bar')
    assert op.operation == 'foo'
    assert op.key_or_keys == 'bar'


def test_CacheOperation_keys():
    op = CacheOperation('foo', ['bar', 'baz'])
    assert op.operation == 'foo'
    assert op.key_or_keys == ['bar', 'baz']


def test_CacheOperation_invalid():
    with pytest.raises(ValueError):
        op = CacheOperation('foo', object())
