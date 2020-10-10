from django_perf_rec.sql import sql_fingerprint


def test_empty():
    assert sql_fingerprint("") == ""
    assert sql_fingerprint("\n\n    \n") == ""


def test_select():
    assert sql_fingerprint("SELECT `f1`, `f2` FROM `b`") == "SELECT ... FROM `b`"


def test_select_show_columns(settings):
    assert (
        sql_fingerprint("SELECT `f1`, `f2` FROM `b`", hide_columns=False)
        == "SELECT `f1`, `f2` FROM `b`"
    )


def test_select_limit(settings):
    assert (
        sql_fingerprint("SELECT `f1`, `f2` FROM `b` LIMIT 12", hide_columns=False)
        == "SELECT `f1`, `f2` FROM `b` LIMIT #"
    )


def test_select_coalesce_show_columns(settings):
    assert (
        sql_fingerprint(
            (
                "SELECT `table`.`f1`, COALESCE(table.f2->>'a', table.f2->>'b', "
                + "'default') FROM `table`"
            ),
            hide_columns=False,
        )
        == "SELECT `table`.`f1`, COALESCE(table.f2->>#, table.f2->>#, #) FROM `table`"
    )


def test_select_where():
    assert (
        sql_fingerprint(
            "SELECT DISTINCT `table`.`field` FROM `table` WHERE `table`.`id` = 1"
        )
        == "SELECT DISTINCT `table`.`field` FROM `table` WHERE `table`.`id` = #"
    )


def test_select_where_show_columns(settings):
    assert (
        sql_fingerprint(
            "SELECT DISTINCT `table`.`field` FROM `table` WHERE `table`.`id` = 1",
            hide_columns=False,
        )
        == "SELECT DISTINCT `table`.`field` FROM `table` WHERE `table`.`id` = #"
    )


def test_select_comment():
    assert (
        sql_fingerprint("SELECT /* comment */ `f1`, `f2` FROM `b`")
        == "SELECT /* comment */ ... FROM `b`"
    )


def test_select_comment_show_columns(settings):
    assert (
        sql_fingerprint("SELECT /* comment */ `f1`, `f2` FROM `b`", hide_columns=False)
        == "SELECT /* comment */ `f1`, `f2` FROM `b`"
    )


def test_select_join():
    assert (
        sql_fingerprint(
            "SELECT f1, f2 FROM a INNER JOIN b ON (a.b_id = b.id) WHERE a.f2 = 1"
        )
        == "SELECT ... FROM a INNER JOIN b ON (a.b_id = b.id) WHERE a.f2 = #"
    )


def test_select_join_show_columns(settings):
    assert (
        sql_fingerprint(
            "SELECT f1, f2 FROM a INNER JOIN b ON (a.b_id = b.id) WHERE a.f2 = 1",
            hide_columns=False,
        )
        == "SELECT f1, f2 FROM a INNER JOIN b ON (a.b_id = b.id) WHERE a.f2 = #"
    )


def test_select_order_by():
    assert (
        sql_fingerprint("SELECT f1, f2 FROM a ORDER BY f3")
        == "SELECT ... FROM a ORDER BY f3"
    )


def test_select_order_by_limit():
    assert (
        sql_fingerprint("SELECT f1, f2 FROM a ORDER BY f3 LIMIT 12")
        == "SELECT ... FROM a ORDER BY f3 LIMIT #"
    )


def test_select_order_by_show_columns(settings):
    assert (
        sql_fingerprint("SELECT f1, f2 FROM a ORDER BY f3", hide_columns=False)
        == "SELECT f1, f2 FROM a ORDER BY f3"
    )


def test_select_order_by_multiple():
    assert (
        sql_fingerprint("SELECT f1, f2 FROM a ORDER BY f3, f4")
        == "SELECT ... FROM a ORDER BY f3, f4"
    )


def test_select_group_by():
    assert (
        sql_fingerprint("SELECT f1, f2 FROM a GROUP BY f1")
        == "SELECT ... FROM a GROUP BY f1"
    )


def test_select_group_by_show_columns(settings):
    assert (
        sql_fingerprint("SELECT f1, f2 FROM a GROUP BY f1", hide_columns=False)
        == "SELECT f1, f2 FROM a GROUP BY f1"
    )


def test_select_group_by_multiple():
    assert (
        sql_fingerprint("SELECT f1, f2 FROM a GROUP BY f1, f2")
        == "SELECT ... FROM a GROUP BY f1, f2"
    )


def test_select_group_by_having():
    assert (
        sql_fingerprint("SELECT f1, f2 FROM a GROUP BY f1 HAVING f1 > 21")
        == "SELECT ... FROM a GROUP BY f1 HAVING f1 > #"
    )


def test_select_group_by_having_show_columns(settings):
    assert (
        sql_fingerprint(
            "SELECT f1, f2 FROM a GROUP BY f1 HAVING f1 > 21", hide_columns=False
        )
        == "SELECT f1, f2 FROM a GROUP BY f1 HAVING f1 > #"
    )


def test_select_group_by_having_multiple():
    assert (
        sql_fingerprint("SELECT f1, f2 FROM a GROUP BY f1 HAVING f1 > 21, f2 < 42")
        == "SELECT ... FROM a GROUP BY f1 HAVING f1 > #, f2 < #"
    )


def test_insert():
    assert (
        sql_fingerprint("INSERT INTO `table` (`f1`, `f2`) VALUES ('v1', 2)")
        == "INSERT INTO `table` (...) VALUES (...)"
    )


def test_insert_show_columns(settings):
    assert (
        sql_fingerprint(
            "INSERT INTO `table` (`f1`, `f2`) VALUES ('v1', 2)", hide_columns=False
        )
        == "INSERT INTO `table` (`f1`, `f2`) VALUES (#, #)"
    )


def test_update():
    assert (
        sql_fingerprint("UPDATE `table` SET `foo` = 'bar' WHERE `table`.`id` = 1")
        == "UPDATE `table` SET ... WHERE `table`.`id` = #"
    )


def test_declare_cursor():
    assert (
        sql_fingerprint(
            'DECLARE "_django_curs_140239496394496_1300" NO SCROLL CURSOR WITHOUT'
        )
        == 'DECLARE "_django_curs_#" NO SCROLL CURSOR WITHOUT'
    )


def test_savepoint():
    assert sql_fingerprint("SAVEPOINT `s140323809662784_x54`") == "SAVEPOINT `#`"


def test_rollback_to_savepoint():
    assert (
        sql_fingerprint("ROLLBACK TO SAVEPOINT `s140323809662784_x54`")
        == "ROLLBACK TO SAVEPOINT `#`"
    )


def test_release_savepoint():
    assert (
        sql_fingerprint("RELEASE SAVEPOINT `s140699855320896_x17`")
        == "RELEASE SAVEPOINT `#`"
    )


def test_null_value():
    assert (
        sql_fingerprint(
            "SELECT `f1`, `f2` FROM `b` WHERE `b`.`name` IS NULL", hide_columns=False
        )
        == "SELECT `f1`, `f2` FROM `b` WHERE `b`.`name` IS #"
    )


def test_strip_duplicate_whitespaces():
    assert (
        sql_fingerprint(
            "SELECT    `f1`,  `f2` FROM  `b` WHERE   `b`.`f1` IS  NULL LIMIT 12  "
        )
        == "SELECT ... FROM `b` WHERE `b`.`f1` IS # LIMIT #"
    )


def test_strip_duplicate_whitespaces_recursive():
    assert (
        sql_fingerprint(
            "SELECT    `f1`,  `f2`, (   COALESCE(b.f3->>'en',   b.f3->>'fr', '')) "
            "FROM  `b` WHERE   (`b`.`f1` IS   NULL OR (  EXISTS COUNT(1) )) LIMIT 12  ",
            hide_columns=False,
        )
        == "SELECT `f1`, `f2`, (COALESCE(b.f3->>#, b.f3->>#, #)) "
        "FROM `b` WHERE (`b`.`f1` IS # OR (EXISTS COUNT(#))) LIMIT #"
    )


def test_strip_newlines():
    assert (
        sql_fingerprint("SELECT `f1`, `f2`\nFROM `b`\n LIMIT 12\n\n")
        == "SELECT ... FROM `b` LIMIT #"
    )


def test_strip_raw_query():
    assert (
        sql_fingerprint(
            """
SELECT 'f1'
    , 'f2'
    , 'f3'
FROM "table_a" WHERE "table_a"."f1" = 1 OR (
"table_a"."type" = 'A' AND
EXISTS (
    SELECT "table_b"."id"
    FROM "table_b"
    WHERE "table_b"."id" = 1
) = true)
"""
        )
        == (
            'SELECT ... FROM "table_a" WHERE "table_a"."f1" = # OR '
            + '("table_a"."type" = # AND EXISTS (SELECT "table_b"."id" FROM '
            + '"table_b" WHERE "table_b"."id" = # ) = true)'
        )
    )


def test_in_single_value():
    assert (
        sql_fingerprint("SELECT `f1`, `f2` FROM `b` WHERE `x` IN (1)")
        == "SELECT ... FROM `b` WHERE `x` IN (#)"
    )


def test_in_multiple_values():
    assert (
        sql_fingerprint("SELECT `f1`, `f2` FROM `b` WHERE `x` IN (1, 2, 3)")
        == "SELECT ... FROM `b` WHERE `x` IN (...)"
    )


def test_in_multiple_clauses():
    assert (
        sql_fingerprint(
            "SELECT `f1`, `f2` FROM `b` WHERE `x` IN (1, 2, 3) AND `y` IN (4, 5, 6)"
        )
        == "SELECT ... FROM `b` WHERE `x` IN (...) AND `y` IN (...)"
    )


def test_in_multiple_values_and_clause():
    assert (
        sql_fingerprint(
            "SELECT `f1`, `f2` FROM `b` WHERE `x` IN (1, 2, 3) AND (`y` = 1 OR `y` = 2)"
        )
        == "SELECT ... FROM `b` WHERE `x` IN (...) AND (`y` = # OR `y` = #)"
    )


def test_in_subquery():
    assert (
        sql_fingerprint("SELECT `f1`, `f2` FROM `b` WHERE `x` IN (SELECT 1)")
        == "SELECT ... FROM `b` WHERE `x` IN (SELECT #)"
    )
