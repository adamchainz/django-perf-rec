from __future__ import annotations

import random

import pytest

from django_perf_rec import record
from tests.utils import run_query

pytestmark = [pytest.mark.django_db(databases=("default", "second"))]

VALUES = [42, 73, 1337]
random.shuffle(VALUES)


@pytest.mark.parametrize("query_param", VALUES)
def test_with_parametrize(request, query_param):
    with record():
        run_query("default", f"SELECT {query_param}")
