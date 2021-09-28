from traceback import extract_stack

import pytest

from django_perf_rec.operation import Operation
from tests.cases import SimpleTestCase


class OperationTests(SimpleTestCase):
    def test_name(self):
        operation = Operation("hi", "world", extract_stack())

        with pytest.raises(TypeError):
            operation.name
