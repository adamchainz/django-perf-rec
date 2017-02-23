# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import django
import patchy
from django.db.models.deletion import get_candidate_relations_to_delete
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.db.models.sql.query import Query


def patch_ORM_to_be_deterministic():
    """
    Django's ORM is non-deterministic with regards to the queries it outputs
    for e.g. OR clauses. We need it to be deterministic so that we can compare
    queries between runs, so we make a couple patches to its internals to do
    this. Mostly this is done by adding sorted() in some places so we're not
    affected by the vagaries of random dict iteration order.

    There is no undo for this, but it doesn't make the ORM much slower or
    anything bad.
    """
    if patch_ORM_to_be_deterministic.have_patched:
        return
    patch_ORM_to_be_deterministic.have_patched = True

    patch_QuerySet()
    patch_Query()
    patch_Q()

    if django.VERSION[:2] <= (1, 9):
        patch_delete()


patch_ORM_to_be_deterministic.have_patched = False


def patch_QuerySet():
    patchy.patch(QuerySet.annotate, """\
        @@ -17,7 +17,7 @@
                 except (AttributeError, TypeError):
                     raise TypeError("Complex annotations require an alias")
                 annotations[arg.default_alias] = arg
        -    annotations.update(kwargs)
        +    annotations.update(sorted(kwargs.items()))

             clone = self._clone()
             names = self._fields
    """)


def patch_Query():
    patchy.patch(Query.add_extra, """\
        @@ -13,7 +13,7 @@
                     param_iter = iter(select_params)
                 else:
                     param_iter = iter([])
        -        for name, entry in select.items():
        +        for name, entry in sorted(select.items()):
                     entry = force_text(entry)
                     entry_params = []
                     pos = entry.find("%s")
    """)


def patch_Q():
    # This one can't be done by patchy since __init__ is different in Python 3,
    # maybe one day https://github.com/adamchainz/patchy/issues/31 will be
    # fixed.
    def __init__(self, *args, **kwargs):
        super(Q, self).__init__(children=list(args) + sorted(kwargs.items()))
    Q.__init__ = __init__


def patch_delete():
    patchy.patch(get_candidate_relations_to_delete, """\
@@ -4,9 +4,12 @@ def get_candidate_relations_to_delete(opts):
     candidate_models = {opts}
     candidate_models = candidate_models.union(opts.concrete_model._meta.proxied_children)
     # For each model, get all candidate fields.
-    candidate_model_fields = set(chain.from_iterable(
-        opts.get_fields(include_hidden=True) for opts in candidate_models
-    ))
+    from collections import OrderedDict
+    candidates_dict = OrderedDict()
+    for opts in candidate_models:
+        for field in opts.get_fields(include_hidden=True):
+            candidates_dict[field.name] = field
+    candidate_model_fields = candidates_dict.values()
     # The candidate relations are the ones that come from N-1 and 1-1 relations.
     # N-N  (i.e., many-to-many) relations aren't candidates for deletion.
     return (
""")
