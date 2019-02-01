from django.db.backends.sqlite3.base import DatabaseWrapper as OrigDatabaseWrapper

from .operations import DatabaseOperations


class DatabaseWrapper(OrigDatabaseWrapper):

    def __init__(self, *args, **kwargs):
        super(DatabaseWrapper, self).__init__(*args, **kwargs)
        self.ops = DatabaseOperations(self)
