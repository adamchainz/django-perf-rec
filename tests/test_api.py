import os

import pytest
from django.core.cache import caches
from django.db.models import Q
from django.db.models.functions import Upper
from django.test import SimpleTestCase, TestCase, override_settings

from django_perf_rec import TestCaseMixin, get_perf_path, get_record_name, record
from tests.testapp.models import Author
from tests.utils import pretend_not_under_pytest, run_query, temporary_path

FILE_DIR = os.path.dirname(__file__)


class RecordTests(TestCase):
    def test_single_db_query(self):
        with record():
            run_query("default", "SELECT 1337")

    def test_single_db_query_model(self):
        with record():
            list(Author.objects.all())

    @override_settings(PERF_REC={"HIDE_COLUMNS": False})
    def test_single_db_query_model_with_columns(self):
        with record():
            list(Author.objects.all())

    def test_multiple_db_queries(self):
        with record():
            run_query("default", "SELECT 1337")
            run_query("default", "SELECT 4949")

    def test_non_deterministic_QuerySet_annotate(self):
        with record():
            list(Author.objects.annotate(x=Upper("name"), y=Upper("name")))

    def test_non_deterministic_QuerySet_extra(self):
        with record():
            list(Author.objects.extra(select={"x": "1", "y": "1"}))

    def test_non_deterministic_Q_query(self):
        with record():
            list(Author.objects.filter(Q(name="foo", age=1)))

    def test_single_cache_op(self):
        with record():
            caches["default"].get("foo")

    def test_multiple_cache_ops(self):
        with record():
            caches["default"].set("foo", "bar")
            caches["second"].get_many(["foo", "bar"])
            caches["default"].delete("foo")

    def test_multiple_calls_in_same_function_are_different_records(self):
        with record():
            caches["default"].get("foo")

        with record():
            caches["default"].get("bar")

    def test_custom_name(self):
        with record(record_name="custom"):
            caches["default"].get("foo")

    def test_custom_name_multiple_calls(self):
        with record(record_name="custom"):
            caches["default"].get("foo")

        with pytest.raises(AssertionError) as excinfo:
            with record(record_name="custom"):
                caches["default"].get("bar")

        assert "Performance record did not match" in str(excinfo.value)

    def test_diff(self):
        with pretend_not_under_pytest():
            with record(record_name="test_diff"):
                caches["default"].get("foo")

            with pytest.raises(AssertionError) as excinfo:
                with record(record_name="test_diff"):
                    caches["default"].get("bar")

            msg = str(excinfo.value)
            assert "- cache|get: foo\n" in msg
            assert "+ cache|get: bar\n" in msg

    def test_path_pointing_to_filename(self):
        with temporary_path("custom.perf.yml"):

            with record(path="custom.perf.yml"):
                caches["default"].get("foo")

            assert os.path.exists("custom.perf.yml")

    def test_path_pointing_to_filename_record_twice(self):
        with temporary_path("custom.perf.yml"):

            with record(path="custom.perf.yml"):
                caches["default"].get("foo")

            with record(path="custom.perf.yml"):
                caches["default"].get("foo")

    def test_path_pointing_to_dir(self):
        temp_dir = os.path.join(FILE_DIR, "perf_files/")
        with temporary_path(temp_dir):

            with record(path="perf_files/"):
                caches["default"].get("foo")

            full_path = os.path.join(FILE_DIR, "perf_files", "test_api.perf.yml")
            assert os.path.exists(full_path)

    def test_custom_nested_path(self):
        temp_dir = os.path.join(FILE_DIR, "perf_files/")
        with temporary_path(temp_dir):

            with record(path="perf_files/api/"):
                caches["default"].get("foo")

            full_path = os.path.join(FILE_DIR, "perf_files", "api", "test_api.perf.yml")
            assert os.path.exists(full_path)

    @override_settings(PERF_REC={"MODE": "once"})
    def test_mode_once(self):
        temp_dir = os.path.join(FILE_DIR, "perf_files/")
        with temporary_path(temp_dir):

            with record(path="perf_files/api/"):
                caches["default"].get("foo")

            full_path = os.path.join(FILE_DIR, "perf_files", "api", "test_api.perf.yml")
            assert os.path.exists(full_path)

    @override_settings(PERF_REC={"MODE": "none"})
    def test_mode_none(self):
        temp_dir = os.path.join(FILE_DIR, "perf_files/")
        with temporary_path(temp_dir):

            with pytest.raises(AssertionError) as excinfo:

                with record(path="perf_files/api/"):
                    caches["default"].get("foo")

            assert "Original performance record does not exist" in str(excinfo.value)

            full_path = os.path.join(FILE_DIR, "perf_files", "api", "test_api.perf.yml")
            assert not os.path.exists(full_path)

    @override_settings(PERF_REC={"MODE": "all"})
    def test_mode_all(self):
        temp_dir = os.path.join(FILE_DIR, "perf_files/")
        with temporary_path(temp_dir):

            with pytest.raises(AssertionError) as excinfo:

                with record(path="perf_files/api/"):
                    caches["default"].get("foo")

            assert "Original performance record did not exist" in str(excinfo.value)

            full_path = os.path.join(FILE_DIR, "perf_files", "api", "test_api.perf.yml")
            assert os.path.exists(full_path)

    def test_delete_on_cascade_called_twice(self):
        arthur = Author.objects.create(name="Arthur", age=42)
        with record():
            arthur.delete()


class GetPerfPathTests(SimpleTestCase):
    def test_py_file(self):
        assert get_perf_path("foo.py") == "foo.perf.yml"

    def test_pyc_file(self):
        assert get_perf_path("foo.pyc") == "foo.perf.yml"

    def test_unknown_file(self):
        assert get_perf_path("foo.plob") == "foo.plob.perf.yml"


class GetRecordNameTests(SimpleTestCase):
    def test_class_and_test(self):
        assert (
            get_record_name(class_name="FooTests", test_name="test_bar")
            == "FooTests.test_bar"
        )

    def test_just_test(self):
        assert get_record_name(test_name="test_baz") == "test_baz"

    def test_multiple_calls(self):
        assert get_record_name(test_name="test_qux") == "test_qux"
        assert get_record_name(test_name="test_qux") == "test_qux.2"

    def test_multiple_calls_from_different_files(self):
        assert get_record_name(test_name="test_qux", file_name="foo.py") == "test_qux"

        assert get_record_name(test_name="test_qux", file_name="foo2.py") == "test_qux"

        assert get_record_name(test_name="test_qux", file_name="foo.py") == "test_qux"

        assert get_record_name(test_name="test_qux", file_name="foo.py") == "test_qux.2"


class TestCaseMixinTests(TestCaseMixin, TestCase):
    def test_record_performance(self):
        with self.record_performance():
            caches["default"].get("foo")

    def test_record_performance_record_name(self):
        with self.record_performance(record_name="other"):
            caches["default"].get("foo")

    def test_record_performance_file_name(self):
        perf_name = __file__.replace(".py", ".file_name.perf.yml")
        with self.record_performance(path=perf_name):
            caches["default"].get("foo")
