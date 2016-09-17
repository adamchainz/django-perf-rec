# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import inspect
from collections import namedtuple


TestDetails = namedtuple('TestDetails', ['file_path', 'class_name', 'test_name'])


def current_test():
    """
    Use a little harmless stack inspection to determine the test that is currently running.
    """
    frame = inspect.currentframe()
    try:
        while True:
            if frame.f_code.co_name.startswith('test_'):
                break

            # Next frame
            frame = frame.f_back
            if frame is None:
                break

        if frame is None:
            raise RuntimeError("Could not automatically determine the test name.")

        file_path = frame.f_globals['__file__']

        # May be a pytest function test so we can't assume 'self' exists
        its_self = frame.f_locals.get('self', None)
        if its_self is None:
            class_name = None
        else:
            class_name = its_self.__class__.__name__

        test_name = frame.f_code.co_name

        return TestDetails(
            file_path=file_path,
            class_name=class_name,
            test_name=test_name,
        )
    finally:
        # Always delete frame references to help garbage collector
        del frame


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
