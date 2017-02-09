.. :changelog:

History
=======

Pending release
---------------

* New release notes go here

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
