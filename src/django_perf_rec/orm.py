import patchy
from django.db.models.query import QuerySet
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


patch_ORM_to_be_deterministic.have_patched = False


def patch_QuerySet():
    patchy.patch(
        QuerySet.annotate,
        """\
        @@ -17,7 +17,7 @@
                 except (AttributeError, TypeError):
                     raise TypeError("Complex annotations require an alias")
                 annotations[arg.default_alias] = arg
        -    annotations.update(kwargs)
        +    annotations.update(sorted(kwargs.items()))

             clone = self._clone()
             names = self._fields
    """,
    )


def patch_Query():
    patchy.patch(
        Query.add_extra,
        """\
        @@ -13,7 +13,7 @@
                     param_iter = iter(select_params)
                 else:
                     param_iter = iter([])
        -        for name, entry in select.items():
        +        for name, entry in sorted(select.items()):
                     entry = str(entry)
                     entry_params = []
                     pos = entry.find("%s")
    """,
    )
