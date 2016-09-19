# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django.db import connections


def run_query(alias, sql, params=None):
    with connections[alias].cursor() as cursor:
        cursor.execute(sql, params)
