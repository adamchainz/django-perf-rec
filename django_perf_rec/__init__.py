# -*- coding:utf-8 -*-
"""
isort:skip_file
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import six

try:
    import pytest
except ImportError:
    pytest = None

if pytest is not None:
    if six.PY2:
        pytest.register_assert_rewrite(b'django_perf_rec.api')
    else:
        pytest.register_assert_rewrite('django_perf_rec.api')

from .api import TestCaseMixin, record  # noqa: F401

__version__ = '1.0.4'
