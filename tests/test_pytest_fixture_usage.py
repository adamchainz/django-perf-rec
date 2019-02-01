import pytest

from django_perf_rec import get_perf_path, get_record_name, record

from .utils import run_query

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def record_auto_name():
    with record():
        yield


def test_auto_name(record_auto_name):
    run_query('default', 'SELECT 1337')


@pytest.fixture
def record_auto_name_with_request(request):
    with record():
        yield


def test_auto_name_with_request(record_auto_name_with_request):
    run_query('default', 'SELECT 1337')


@pytest.fixture
def record_build_name(request):
    record_name = get_record_name(
        class_name=request.cls.__name__ if request.cls is not None else None,
        test_name=request.function.__name__,
    )
    path = get_perf_path(file_path=request.fspath.strpath)
    with record(record_name=record_name, path=path):
        yield


def test_build_name(record_build_name):
    run_query('default', 'SELECT 1337')
