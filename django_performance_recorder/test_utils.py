# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


from django.test import SimpleTestCase

from django_performance_recorder.utils import sorted_names


class SortedNamesTests(SimpleTestCase):

    def test_empty(self):
        assert sorted_names([]) == []

    def test_just_default(self):
        assert sorted_names(['default']) == ['default']

    def test_just_something(self):
        assert sorted_names(['something']) == ['something']

    def test_does_sort(self):
        assert sorted_names(['b', 'a']) == ['a', 'b']

    def test_sort_keeps_default_first(self):
        assert sorted_names(['a', 'default']) == ['default', 'a']
