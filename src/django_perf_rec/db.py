from functools import wraps
from types import MethodType

from django.db import connections

from django_perf_rec.operation import AllSourceRecorder, Operation
from django_perf_rec.orm import patch_ORM_to_be_deterministic
from django_perf_rec.settings import perf_rec_settings
from django_perf_rec.sql import sql_fingerprint


class DBOp(Operation):
    def __repr__(self):
        return "DBOp({!r}, {!r})".format(repr(self.alias), repr(self.query))


class DBRecorder:
    """
    Monkey-patch-wraps a database connection to call 'callback' on every
    query it runs.
    """

    def __init__(self, alias, callback):
        self.alias = alias
        self.callback = callback

    def __enter__(self):
        """
        When using the debug cursor wrapper, Django calls
        connection.ops.last_executed_query to get the SQL from the client
        library. Here we wrap this function on the connection to grab the SQL
        as it comes out.
        """
        patch_ORM_to_be_deterministic()

        connection = connections[self.alias]
        self.orig_force_debug_cursor = connection.force_debug_cursor
        connection.force_debug_cursor = True

        def call_callback(func):
            alias = self.alias
            callback = self.callback

            @wraps(func)
            def inner(self, *args, **kwargs):
                sql = func(*args, **kwargs)
                hide_columns = perf_rec_settings.HIDE_COLUMNS
                callback(
                    DBOp(
                        alias=alias,
                        query=sql_fingerprint(sql, hide_columns=hide_columns),
                    )
                )
                return sql

            return inner

        self.orig_last_executed_query = connection.ops.last_executed_query
        connection.ops.last_executed_query = MethodType(
            call_callback(connection.ops.last_executed_query), connection.ops
        )

    def __exit__(self, exc_type, exc_value, exc_traceback):
        connection = connections[self.alias]
        connection.force_debug_cursor = False
        connection.ops.last_executed_query = self.orig_last_executed_query


class AllDBRecorder(AllSourceRecorder):
    """
    Launches DBRecorders on all database connections
    """

    sources_setting = "DATABASES"
    recorder_class = DBRecorder
