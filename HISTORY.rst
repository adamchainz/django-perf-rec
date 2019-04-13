.. :changelog:

History
=======

Pending release
---------------

.. Insert new release notes below this line

4.2.0 (2019-04-13)
------------------

* Work with, and require, ``sqlparse`` > 0.3.0.

4.1.0 (2019-03-04)
------------------

* Fix a bug in automatic test record naming when two different modules had a
  test with the same class + name that ran one after another.
* Fix Python 3.7 ``DeprecationWarning`` for ``collections.abc`` (Python 3.7 not
  officially supported yet).

4.0.0 (2019-02-01)
------------------

* Drop Python 2 support, only Python 3.4+ is supported now.
* Drop Django 1.8, 1.9, and 1.10 support. Only Django 1.11+ is supported now.
* Dropped requirements for ``kwargs-only`` and ``six``.

3.1.1 (2018-12-03)
------------------

* Fix to actually obey the ``HIDE_COLUMNS`` option.

3.1.0 (2018-12-02)
------------------

* Add the ``HIDE_COLUMNS`` option in settings to disable replacing column lists
  with ``...`` in all places.

3.0.0 (2018-07-17)
------------------

* Don't replace columns in ORDER BY, GROUP BY and HAVING clauses.

2.2.0 (2018-01-24)
------------------

* Use ``kwargs-only`` library rather than vendored copy.
* Erase volatile part of PostgreSQL cursor name.

2.1.0 (2017-05-29)
------------------

* Exposed the automatic naming logic used in ``record()`` in two new functions
  ``get_perf_path()`` and ``get_record_name()``, in order to ease creation of
  test records from calls outside of tests.
* Made the automatic test detection work when running under a Pytest fixture.
* Stopped throwing warnings on Python 3.
* Fixed loading empty performance record files.

2.0.1 (2017-03-02)
------------------

* Make cascaded delete queries deterministic on Django <1.10, with another
  Patchy patch to make it match the order from 1.10+.

2.0.0 (2017-02-09)
------------------

* Arguments to ``record`` must be passed as keyword arguments.
* ``file_name`` is removed as an argument to ``record`` following its
  deprecation in release 1.1.0.


1.1.1 (2016-10-30)
------------------

* Fix django session keys not being fingerprinted.
* Show diff when records don't match (when not on pytest).
* Add new 'MODE' setting with three modes. This allows customization of the
  behaviour for missing performance records. The new ``'none'`` mode is
  particularly useful for CI servers as it makes tests fail if their
  corresponding performance records have not been committed.

1.1.0 (2016-10-26)
------------------

* Fix automatic filenames for tests in ``.pyc`` files.
* Add the ``path`` argument to ``record`` which allows specifying a relative
  directory or filename to use. This deprecates the ``file_name`` argument,
  which will be removed in a future major release. For more info see the
  README.

1.0.4 (2016-10-23)
------------------

* Work with ``sqlparse`` 0.2.2

1.0.3 (2016-10-07)
------------------

* Stopped ``setup.py`` installing ``tests`` module.

1.0.2 (2016-09-23)
------------------

* Confirmed Django 1.8 and 1.10 support.

1.0.1 (2016-09-20)
------------------

* Fix ``install_requires`` in ``setup.py``.

1.0.0 (2016-09-19)
------------------

* Initial version with ``record()`` that can record database queries and cache
  operations and error if they change between test runs.
