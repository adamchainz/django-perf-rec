from __future__ import annotations

import pytest

from django_perf_rec import record
from tests.utils import run_query

pytestmark = [pytest.mark.django_db(databases=("default", "second"))]


@pytest.mark.parametrize("query_param", [42, 73, 1337])
def test_with_parametrize(request, query_param):
    with record():
        run_query("default", f"SELECT {query_param}")
