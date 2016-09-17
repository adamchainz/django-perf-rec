# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


def sorted_names(names):
    """
    Sort a list of names but keep the word 'default' first if it's there.
    """
    names = list(names)

    have_default = False
    if 'default' in names:
        names.remove('default')
        have_default = True

    sorted_names = sorted(names)

    if have_default:
        sorted_names = ['default'] + sorted_names

    return sorted_names
