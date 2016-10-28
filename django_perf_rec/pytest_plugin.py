# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

in_pytest = False


def pytest_configure(config):
    global in_pytest
    in_pytest = True
