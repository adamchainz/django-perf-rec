from django.test import SimpleTestCase

from django_perf_rec import pytest_plugin

from .utils import pretend_not_under_pytest


class PytestPluginTests(SimpleTestCase):

    def test_in_pytest(self):
        # We always run our tests in pytest
        assert pytest_plugin.in_pytest

    def test_in_pytest_pretend(self):
        # The test helper should work to ignore it
        with pretend_not_under_pytest():
            assert not pytest_plugin.in_pytest
