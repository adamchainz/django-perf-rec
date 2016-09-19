# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django.db.backends.sqlite3.operations import DatabaseOperations as OrigDatabaseOperations


class DatabaseOperations(OrigDatabaseOperations):

    # From Django commit 4f6a7663bcddffb114f2647f9928cbf1fdd8e4b5

    def _quote_params_for_last_executed_query(self, params):
        """
        Only for last_executed_query! Don't use this to execute SQL queries!
        """
        sql = 'SELECT ' + ', '.join(['QUOTE(?)'] * len(params))
        # Bypass Django's wrappers and use the underlying sqlite3 connection
        # to avoid logging this query - it would trigger infinite recursion.
        cursor = self.connection.connection.cursor()
        # Native sqlite3 cursors cannot be used as context managers.
        try:
            return cursor.execute(sql, params).fetchone()
        finally:
            cursor.close()

    def last_executed_query(self, cursor, sql, params):
        # Python substitutes parameters in Modules/_sqlite/cursor.c with:
        # pysqlite_statement_bind_parameters(self->statement, parameters, allow_8bit_chars);
        # Unfortunately there is no way to reach self->statement from Python,
        # so we quote and substitute parameters manually.
        if params:
            if isinstance(params, (list, tuple)):
                params = self._quote_params_for_last_executed_query(params)
            else:
                keys = params.keys()
                values = tuple(params.values())
                values = self._quote_params_for_last_executed_query(values)
                params = dict(zip(keys, values))
            return sql % params
        # For consistency with SQLiteCursorWrapper.execute(), just return sql
        # when there are no parameters. See #13648 and #17158.
        else:
            return sql
