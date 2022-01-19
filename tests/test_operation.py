from __future__ import annotations

from traceback import extract_stack

import pytest
from django.test import SimpleTestCase

from django_perf_rec.operation import Operation


class OperationTests(SimpleTestCase):
    def test_name(self):
        operation = Operation("hi", "world", extract_stack())

        with pytest.raises(TypeError):
            operation.name
