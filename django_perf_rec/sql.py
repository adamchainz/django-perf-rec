# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import six
from django.utils.lru_cache import lru_cache
from sqlparse import parse, tokens
from sqlparse.sql import IdentifierList, Token


@lru_cache(maxsize=500)
def sql_fingerprint(query):
    """
    Simplify a query, taking away exact values and fields selected.

    Imperfect but better than super explicit, value-dependent queries.
    """
    parsed_query = parse(query)[0]
    sql_recursively_simplify(parsed_query)
    return six.text_type(parsed_query)


sql_deleteable_tokens = (
    tokens.Number,
    tokens.Number.Float,
    tokens.Number.Integer,
    tokens.Number.Hexadecimal,
    tokens.String,
    tokens.String.Single,
)


def sql_recursively_simplify(node):
    # Erase which fields are being updated in an UPDATE
    if node.tokens[0].value == 'UPDATE':
        i_set = [i for (i, t) in enumerate(node.tokens) if t.value == 'SET'][0]
        i_where = [i for (i, t) in enumerate(node.tokens)
                   if _is_group(t) and t.tokens[0].value == 'WHERE'][0]
        middle = [Token(tokens.Punctuation, ' ... ')]
        node.tokens = node.tokens[:i_set + 1] + middle + node.tokens[i_where:]

    # Erase the names of savepoints since they are non-deteriministic
    if hasattr(node, 'tokens'):
        # SAVEPOINT x
        if str(node.tokens[0]) == 'SAVEPOINT':
            node.tokens[2].tokens[0].value = '`#`'
            return
        # RELEASE SAVEPOINT x
        elif len(node.tokens) >= 3 and node.tokens[2].value == 'SAVEPOINT':
            node.tokens[4].tokens[0].value = "`#`"
            return
        # ROLLBACK TO SAVEPOINT X
        token_values = [getattr(t, 'value', '') for t in node.tokens]
        if len(node.tokens) == 7 and token_values[:6] == ['ROLLBACK', ' ', 'TO', ' ', 'SAVEPOINT', ' ']:
            node.tokens[6].tokens[0].value = '`#`'
            return

    for i, token in enumerate(node.tokens):
        ttype = getattr(token, 'ttype', None)

        if isinstance(token, IdentifierList):
            token.tokens = [Token(tokens.Punctuation, '...')]
        elif hasattr(token, 'tokens'):
            sql_recursively_simplify(token)
        elif ttype in sql_deleteable_tokens:
            token.value = '#'
        elif ttype == tokens.Whitespace.Newline:
            token.value = ''  # Erase newlines
        elif ttype == tokens.Whitespace:
            token.value = ' '
        elif getattr(token, 'value', None) == 'NULL':
            token.value = '#'


def _is_group(token):
    """
    sqlparse 0.2.2 changed it from a callable to a bool property
    """
    is_group = token.is_group
    if isinstance(is_group, bool):
        return is_group
    else:
        return is_group()
