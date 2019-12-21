import pytest

from django_perf_rec import record
from tests.utils import run_query

pytestmark = [pytest.mark.django_db]


def test_duplicate_name():
    with record():
        run_query("default", "SELECT 1337")
