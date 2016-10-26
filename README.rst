===============
django-perf-rec
===============

.. image:: https://img.shields.io/pypi/v/django-perf-rec.svg
    :target: https://pypi.python.org/pypi/django-perf-rec

.. image:: https://img.shields.io/travis/YPlan/django-perf-rec/master.svg
        :target: https://travis-ci.org/YPlan/django-perf-rec

"Keep detailed records of the performance of your Django code."

**django-perf-rec** is like Django's ``assertNumQueries`` on steroids. It lets
you track the individual queries and cache operations that occur in your code.
Use it in your tests like so:

.. code-block:: python

    def test_home(self):
        with django_perf_rec.record():
            self.client.get('/')

It then stores a YAML file alongside the test file that tracks the queries and
operations, looking something like:

.. code-block:: yaml

    MyTests.test_home:
    - cache|get: home_data
    - db: 'SELECT ... FROM myapp_table WHERE (myapp_table.id = #)'
    - db: 'SELECT ... FROM myapp_table WHERE (myapp_table.id = #)'

When the test is run again, the new record will be compared with the one in the
YAML file. If they are different, an assertion failure will be raised, failing
the test. Magic!

Just check the YAML file in alongside your test and you have unbreakable
performance with much better information about any regressions compared to
``assertNumQueries``. If you are fine with the changes from a failing test,
just remove the file and rerun the test to regenerate it.

We also have an `introductory blog
post <https://tech.yplanapp.com/2016/09/26/introducing-django-perf-rec/>`_ that
says a little more about why we made it.

Installation
============

Use **pip**:

.. code-block:: bash

    pip install django-perf-rec

Requirements
============

Tested with all combinations of:

* Python: 2.7, 3.5
* Django: 1.8, 1.9, 1.10

API
===

``record(file_name=None, record_name=None, path=None)``
-------------------------------------------------------

Return a context manager that will be used for a single performance test.

``path`` is the path to a directory or file in which to store the record. If it
ends with ``'/'``, or is left as ``None``, the filename will be automatically
determined by looking at the filename the calling code is in and replacing the
``.py[c]`` extension with ``.perf.yml``. If it points to a directory that
doesn't exist, that directory will be created.

``record_name`` is the name of the record inside the performance file to use.
If left as ``None``, the code assumes you are inside a Django ``TestCase`` and
uses magic stack inspection to find that test case, and uses a name based upon
the test case name + the test method name + an optional counter if you invoke
``record()`` multiple times inside the same test method.

``file_name`` is deprecated in favour of ``path`` and will be removed in a
future major release. It can be used to point to the filename in which the
record should be stored, which ``path`` supports too.

Whilst open, the context manager tracks all DB queries on all connections, and
all cache operations on all defined caches. It names the connection/cache in
the tracked operation it uses, except from for the ``default`` one.

When the context manager exits, it will use the list of operations it has
gathered. If the file ``file_name`` doesn't exist, or doesn't contain data for
the specific ``record_name``, it will be created and saved and the test will
pass with no assertions. However if the record **does** exist inside the file,
the collected record will be compared with the original one, and if different,
an ``AssertionError`` will be raised. This currently uses a plain message, but
if you're using `pytest <http://pytest.org/>`_ its assertion rewriting will be
used and make it look pretty.

Example:

.. code-block:: python

    import django_perf_rec

    from app.models import Author

    class AuthorPerformanceTests(TestCase):

        def test_special_method(self):
            with django_perf_rec.record():
                list(Author.objects.special_method())


``TestCaseMixin``
-----------------

A mixin class to be added to your custom ``TestCase`` subclass so you can use
**django-perf-rec** across your codebase without needing to import it in each
individual test file. It adds one method, ``record_performance()``, whose
signature is the same as ``record()`` above.

Example:

.. code-block:: python

    # yplan/test.py
    from django.test import TestCase as OrigTestCase
    from django_perf_rec import TestCaseMixin

    class TestCase(TestCaseMixin, OrigTestCase):
        pass

    # app/tests/models/test_author.py
    from app.models import Author
    from yplan.test import TestCase

    class AuthorPerformanceTests(TestCase):

        def test_special_method(self):
            with self.record_performance():
                list(Author.objects.special_method())
