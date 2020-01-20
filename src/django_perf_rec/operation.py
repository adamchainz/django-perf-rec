
class Operation(object):
    def __init__(self, alias, query):
        self.alias = alias
        self.query = query

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and self.alias == other.alias
            and self.query == other.query
        )
