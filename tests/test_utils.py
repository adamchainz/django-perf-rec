from django.test import SimpleTestCase

from django_perf_rec.utils import current_test, sorted_names


class CurrentTestTests(SimpleTestCase):
    def test_here(self):
        details = current_test()
        assert details.file_path == __file__
        assert details.class_name == "CurrentTestTests"
        assert details.test_name == "test_here"

    def test_twice_same(self):
        assert current_test() == current_test()

    def test_functional(self):
        def test_thats_functional():
            return current_test()

        details = test_thats_functional()
        assert details.file_path == __file__
        assert details.class_name is None
        assert details.test_name == "test_thats_functional"


class SortedNamesTests(SimpleTestCase):
    def test_empty(self):
        assert sorted_names([]) == []

    def test_just_default(self):
        assert sorted_names(["default"]) == ["default"]

    def test_just_something(self):
        assert sorted_names(["something"]) == ["something"]

    def test_does_sort(self):
        assert sorted_names(["b", "a"]) == ["a", "b"]

    def test_sort_keeps_default_first(self):
        assert sorted_names(["a", "default"]) == ["default", "a"]
