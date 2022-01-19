from __future__ import annotations

import shutil
from tempfile import mkdtemp

import pytest
import yaml
from django.test import SimpleTestCase

from django_perf_rec.yaml import KVFile


class KVFileTests(SimpleTestCase):
    def setUp(self):
        super().setUp()
        KVFile._clear_load_cache()
        self.temp_dir = mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        super().tearDown()

    def test_load_no_permissions(self):
        with pytest.raises(IOError):
            KVFile("/")

    def test_load_non_existent_is_empty(self):
        kvf = KVFile(self.temp_dir + "/foo.yml")
        assert len(kvf) == 0
        assert kvf.get("foo", None) is None

    def test_load_existent(self):
        file_name = self.temp_dir + "/foo.yml"
        with open(file_name, "w") as fp:
            fp.write("foo: [{bar: baz}]")

        kvf = KVFile(file_name)
        assert len(kvf) == 1
        assert kvf.get("foo", None) == [{"bar": "baz"}]

    def test_load_empty(self):
        file_name = self.temp_dir + "/foo.yml"
        with open(file_name, "w") as fp:
            fp.write("")

        assert len(KVFile(file_name)) == 0

    def test_load_whitespace_empty(self):
        file_name = self.temp_dir + "/foo.yml"
        with open(file_name, "w") as fp:
            fp.write(" \n")

        assert len(KVFile(file_name)) == 0

    def test_load_non_dictionary(self):
        file_name = self.temp_dir + "/foo.yml"
        with open(file_name, "w") as fp:
            fp.write("[not, a, dictionary]")

        with pytest.raises(TypeError) as excinfo:
            KVFile(file_name)
        assert "not a dictionary" in str(excinfo.value)

    def test_get_after_set_same(self):
        kvf = KVFile(self.temp_dir + "/foo.yml")
        kvf.set_and_save("foo", [{"bar": "baz"}])

        assert len(kvf) == 1
        assert kvf.get("foo", None) == [{"bar": "baz"}]

    def test_load_second_same(self):
        kvf = KVFile(self.temp_dir + "/foo.yml")
        kvf.set_and_save("foo", [{"bar": "baz"}])
        kvf2 = KVFile(self.temp_dir + "/foo.yml")

        assert len(kvf2) == 1
        assert kvf2.get("foo", None) == [{"bar": "baz"}]

    def test_sets_dont_cause_append_duplication(self):
        file_name = self.temp_dir + "/foo.yml"
        kvf = KVFile(file_name)
        kvf.set_and_save("foo", [{"bar": "baz"}])
        kvf.set_and_save("foo2", [{"bar": "baz"}])

        with open(file_name) as fp:
            lines = fp.readlines()
            fp.seek(0)
            data = yaml.safe_load(fp)

        assert len(lines) == 4
        assert data == {
            "foo": [{"bar": "baz"}],
            "foo2": [{"bar": "baz"}],
        }
