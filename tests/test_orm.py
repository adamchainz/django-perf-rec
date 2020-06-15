from django.test import SimpleTestCase

from django_perf_rec.orm import patch_ORM_to_be_deterministic


class PatchORMToBeDeterministicTests(SimpleTestCase):
    def test_call_it(self):
        patch_ORM_to_be_deterministic()

    def test_call_it_again(self):
        patch_ORM_to_be_deterministic()
