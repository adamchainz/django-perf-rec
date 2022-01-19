from __future__ import annotations

import pytest
from django.test.utils import override_settings

from django_perf_rec import record
from tests.utils import run_query

pytestmark = [pytest.mark.django_db(databases=("default", "second", "replica"))]


@override_settings(PERF_REC={"MODE": "none"})
def test_duplicate_name():
    with record():
        run_query("default", "SELECT 1337")
        run_query("default", "SELECT 4997")
        run_query("default", "SELECT 4998")
