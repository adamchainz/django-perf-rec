===============
django-perf-rec
===============

.. image:: https://img.shields.io/github/workflow/status/adamchainz/django-perf-rec/CI/master?style=for-the-badge
   :target: https://github.com/adamchainz/django-perf-rec/actions?workflow=CI

.. image:: https://img.shields.io/pypi/v/django-perf-rec.svg?style=for-the-badge
   :target: https://pypi.org/project/django-perf-rec/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
   :target: https://github.com/psf/black

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=for-the-badge
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit

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
    - cache|get: home_data.user_id.#
    - db: 'SELECT ... FROM myapp_table WHERE (myapp_table.id = #)'
    - db: 'SELECT ... FROM myapp_table WHERE (myapp_table.id = #)'

When the test is run again, the new record will be compared with the one in the
YAML file. If they are different, an assertion failure will be raised, failing
the test. Magic!

The queries and keys are 'fingerprinted', replacing information that seems
variable with `#` and `...`. This is done to avoid spurious failures when e.g.
primary keys are different, random data is used, new columns are added to
tables, etc.

If you check the YAML file in along with your tests, you'll have unbreakable
performance with much better information about any regressions compared to
``assertNumQueries``. If you are fine with the changes from a failing test,
just remove the file and rerun the test to regenerate it.

For more information, see our `introductory blog
post <https://tech.yplanapp.com/2016/09/26/introducing-django-perf-rec/>`_ that
says a little more about why we made it.

Installation
============

Use **pip**:

.. code-block:: bash

    python -m pip install django-perf-rec

Requirements
============

Python 3.6 to 3.9 supported.

Django 2.2 to 3.1 suppported.

----

**Are your tests slow?**
Check out my book `Speed Up Your Django Tests <https://gumroad.com/l/suydt>`__ which covers loads of best practices so you can write faster, more accurate tests.

----

API
===

``record(record_name=None, path=None, capture_traceback=None)``
---------------------------------------------------------------

Return a context manager that will be used for a single performance test.

The arguments must be passed as keyword arguments.

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

Whilst open, the context manager tracks all DB queries on all connections, and
all cache operations on all defined caches. It names the connection/cache in
the tracked operation it uses, except from for the ``default`` one.

When the context manager exits, it will use the list of operations it has
gathered. If the relevant file specified using ``path`` doesn't exist, or
doesn't contain data for the specific ``record_name``, it will be created and
saved and the test will pass with no assertions. However if the record **does**
exist inside the file, the collected record will be compared with the original
one, and if different, an ``AssertionError`` will be raised. When running on
pytest, this will use its fancy assertion rewriting; in other test runners/uses
the full diff will be attached to the message.

Example:

.. code-block:: python

    import django_perf_rec

    from app.models import Author

    class AuthorPerformanceTests(TestCase):

        def test_special_method(self):
            with django_perf_rec.record():
                list(Author.objects.special_method())


``capture_traceback``, if not ``None``, should be a function that takes one
argument, the given DB or cache operation, and returns a ``bool`` indiciating
if a traceback should be captured for the operation (by default, they are not).
Capturing tracebacks allows fine-grained debugging of code paths causing the
operations. Be aware that records differing only by the presence of tracebacks
will not match and cause an ``AssertionError`` to be raised, so it's not
normally suitable to permanently record the tracebacks.

For example, if you wanted to know what code paths query the table
``my_table``, you could use a ``capture_traceback`` function like so:

.. code-block:: python

    def debug_sql_query(operation):
        return "my_tables" in operation.query

    def test_special_method(self):
        with django_perf_rec.record(capture_traceback=debug_sql_query):
            list(Author.objects.special_method())

The performance record herer would include a standard Python traceback attached
to each SQL query containing "my_table".

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

``get_perf_path(file_path)``
----------------------------

Encapsulates the logic used in ``record()`` to form ``path`` from the path of
the file containing the currently running test, mostly swapping '.py' or '.pyc'
for '.perf.yml'. You might want to use this when calling ``record()`` from
somewhere other than inside a test (which causes the automatic inspection to
fail), to match the same filename.

``get_record_name(test_name, class_name=None)``
-----------------------------------------------

Encapsulates the logic used in ``record()`` to form a ``record_name`` from
details of the currently running test. You might want to use this when calling
``record()`` from somewhere other than inside a test (which causes the
automatic inspection to fail), to match the same ``record_name``.

Settings
========

Behaviour can be customized with a dictionary called ``PERF_REC`` in your
Django settings, for example:

.. code-block:: python

    PERF_REC = {
        'MODE': 'once'
    }

The possible keys to this dictionary are explained below.

``HIDE_COLUMNS``
----------------

The ``HIDE_COLUMNS`` setting may be used to change the way **django-perf-rec**
simplifies SQL in the recording files it makes. It takes a boolean:

* ``True`` (default) causes column lists in queries to be collapsed, e.g.
  ``SELECT a, b, c FROM t`` becomes ``SELECT ... FROM t``. This is useful
  because selected columns often don't affect query time in typical
  Django applications, it makes the records easier to read, and they then don't
  need updating every time model fields are changed.
* ``False`` stops the collapsing behaviour, causing all the columns to be
  output in the files.

``MODE``
--------

The ``MODE`` setting may be used to change the way **django-perf-rec** behaves
when a performance record does not exist during a test run.

* ``'once'`` (default) creates missing records silently.
* ``'none'`` raises ``AssertionError`` when a record does not exist. You
  probably want to use this mode in CI, to ensure new tests fail if their
  corresponding performance records were not committed.
* ``'all'`` creates missing records and then raises ``AssertionError``.

Usage in Pytest
===============

If you're using Pytest, you might want to call ``record()`` from within a
Pytest fixture and have it automatically apply to all your tests. We have an
example of this, see the file `test_pytest_fixture_usage.py
<https://github.com/adamchainz/django-perf-rec/blob/master/tests/test_pytest_fixture_usage.py>`_
in the test suite.
