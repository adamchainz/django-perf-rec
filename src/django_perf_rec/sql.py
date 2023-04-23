from __future__ import annotations

from functools import lru_cache
from typing import Container

from sqlparse import parse
from sqlparse import tokens
from sqlparse.sql import Comment
from sqlparse.sql import IdentifierList
from sqlparse.sql import Parenthesis
from sqlparse.sql import Token


@lru_cache(maxsize=500)
def sql_fingerprint(query: str, hide_columns: bool = True) -> str:
    """
    Simplify a query, taking away exact values and fields selected.

    Imperfect but better than super explicit, value-dependent queries.
    """
    parsed_queries = parse(query)

    if not parsed_queries:
        return ""

    parsed_query = sql_recursively_strip(parsed_queries[0])
    sql_recursively_simplify(parsed_query, hide_columns=hide_columns)
    return str(parsed_query).strip()


sql_deleteable_tokens = (
    tokens.Number,
    tokens.Number.Float,
    tokens.Number.Integer,
    tokens.Number.Hexadecimal,
    tokens.String,
    tokens.String.Single,
)


def sql_trim(node: Token, idx: int = 0) -> None:
    tokens = node.tokens
    count = len(tokens)
    min_count = abs(idx)

    while count > min_count and tokens[idx].is_whitespace:
        tokens.pop(idx)
        count -= 1


def sql_strip(node: Token) -> None:
    ws_count = 0

    for token in node.tokens:
        if token.is_whitespace:
            token.value = "" if ws_count > 0 else " "
            ws_count += 1
        else:
            ws_count = 0


def sql_recursively_strip(node: Token) -> Token:
    for sub_node in node.get_sublists():
        sql_recursively_strip(sub_node)

    if isinstance(node, Comment):
        return node

    sql_strip(node)

    # strip duplicate whitespaces between parenthesis
    if isinstance(node, Parenthesis):
        sql_trim(node, 1)
        sql_trim(node, -2)

    return node


def sql_recursively_simplify(node: Token, hide_columns: bool = True) -> None:
    # Erase which fields are being updated in an UPDATE
    if node.tokens[0].value == "UPDATE":
        i_set = [i for (i, t) in enumerate(node.tokens) if t.value == "SET"][0]
        i_wheres = [
            i
            for (i, t) in enumerate(node.tokens)
            if t.is_group and t.tokens[0].value == "WHERE"
        ]
        if i_wheres:
            i_where = i_wheres[0]
            end = node.tokens[i_where:]
        else:
            end = []
        middle = [Token(tokens.Punctuation, " ... ")]
        node.tokens = node.tokens[: i_set + 1] + middle + end

    # Ensure IN clauses with simple value in always simplify to "..."
    if node.tokens[0].value == "WHERE":
        in_token_indices = (i for i, t in enumerate(node.tokens) if t.value == "IN")
        for in_token_index in in_token_indices:
            parenthesis = next(
                t
                for t in node.tokens[in_token_index + 1 :]
                if isinstance(t, Parenthesis)
            )
            if all(
                getattr(t, "ttype", "") in sql_deleteable_tokens
                for t in parenthesis.tokens[1:-1]
            ):
                parenthesis.tokens[1:-1] = [Token(tokens.Punctuation, "...")]

    # Erase the names of savepoints since they are non-deteriministic
    if hasattr(node, "tokens"):
        # SAVEPOINT x
        if str(node.tokens[0]) == "SAVEPOINT":
            node.tokens[2].tokens[0].value = "`#`"
            return
        # RELEASE SAVEPOINT x
        elif len(node.tokens) >= 3 and node.tokens[2].value == "SAVEPOINT":
            node.tokens[4].tokens[0].value = "`#`"
            return
        # ROLLBACK TO SAVEPOINT X
        token_values = [getattr(t, "value", "") for t in node.tokens]
        if len(node.tokens) == 7 and token_values[:6] == [
            "ROLLBACK",
            " ",
            "TO",
            " ",
            "SAVEPOINT",
            " ",
        ]:
            node.tokens[6].tokens[0].value = "`#`"
            return

    # Erase volatile part of PG cursor name
    if node.tokens[0].value.startswith('"_django_curs_'):
        node.tokens[0].value = '"_django_curs_#"'

    prev_word_token = None

    for token in node.tokens:
        ttype = getattr(token, "ttype", None)

        # Detect IdentifierList tokens within an ORDER BY, GROUP BY or HAVING
        # clauses
        inside_order_group_having = match_keyword(
            prev_word_token, ["ORDER BY", "GROUP BY", "HAVING"]
        )
        replace_columns = not inside_order_group_having and hide_columns

        if isinstance(token, IdentifierList) and replace_columns:
            token.tokens = [Token(tokens.Punctuation, "...")]
        elif hasattr(token, "tokens"):
            sql_recursively_simplify(token, hide_columns=hide_columns)
        elif ttype in sql_deleteable_tokens:
            token.value = "#"
        elif getattr(token, "value", None) == "NULL":
            token.value = "#"

        if not token.is_whitespace:
            prev_word_token = token


def match_keyword(token: Token | None, keywords: Container[str]) -> bool:
    """
    Checks if the given token represents one of the given keywords
    """
    if not token:
        return False
    if not token.is_keyword:
        return False

    return token.value.upper() in keywords
