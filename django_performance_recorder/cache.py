# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import re
from collections import Mapping, Sequence

import six


class CacheOperation(object):

    def __init__(self, operation, key_or_keys):
        self.operation = operation
        if isinstance(key_or_keys, six.string_types):
            self.key_or_keys = self.clean_key(key_or_keys)
        elif isinstance(key_or_keys, (Mapping, Sequence)):
            self.key_or_keys = sorted(self.clean_key(k) for k in key_or_keys)
        else:
            raise ValueError("key_or_keys must be a string, mapping, or sequence")

    @classmethod
    def clean_key(cls, key):
        """
        Replace things that look like variables with a '#' so tests aren't affected by random variables
        """
        for var_re in cls.VARIABLE_RES:
            key = var_re.sub('#', key)
        return key

    VARIABLE_RES = (
        # Long random hash
        re.compile(r'\b[0-9a-f]{32}\b'),
        # UUIDs
        re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'),
        # Integers
        re.compile(r'\d+'),
    )
