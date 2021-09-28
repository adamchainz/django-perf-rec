from django.test import SimpleTestCase
from django.test import TestCase as BaseTestCase

__all__ = ("SimpleTestCase", "TestCase")


class TestCase(BaseTestCase):
    databases = ("default", "second", "replica")
