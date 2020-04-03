from django.db.models import Q
from django.test import SimpleTestCase

from django_perf_rec.orm import patch_ORM_to_be_deterministic


class PatchORMToBeDeterministicTests(SimpleTestCase):
    def test_call_it(self):
        patch_ORM_to_be_deterministic()

    def test_call_it_again(self):
        patch_ORM_to_be_deterministic()

    def test_q_connector(self):
        q1 = Q(foo="bar") | Q(bar="foo")
        _path, args, kwargs = q1.deconstruct()
        q2 = Q(*args, **kwargs)
        self.assertEqual(q1, q2)
