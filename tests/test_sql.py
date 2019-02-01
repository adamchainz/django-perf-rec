from django_perf_rec.sql import sql_fingerprint


def test_select():
    assert (
        sql_fingerprint("SELECT `f1`, `f2` FROM `b`") ==
        "SELECT ... FROM `b`"
    )


def test_select_show_columns(settings):
    assert (
        sql_fingerprint("SELECT `f1`, `f2` FROM `b`", hide_columns=False) ==
        "SELECT `f1`, `f2` FROM `b`"
    )


def test_select_where():
    assert (
        sql_fingerprint("SELECT DISTINCT `table`.`field` FROM `table` WHERE `table`.`id` = 1") ==
        "SELECT DISTINCT `table`.`field` FROM `table` WHERE `table`.`id` = #"
    )


def test_select_where_show_columns(settings):
    assert (
        sql_fingerprint("SELECT DISTINCT `table`.`field` FROM `table` WHERE `table`.`id` = 1", hide_columns=False) ==
        "SELECT DISTINCT `table`.`field` FROM `table` WHERE `table`.`id` = #"
    )


def test_select_comment():
    assert (
        sql_fingerprint("SELECT /* comment */ `f1`, `f2` FROM `b`") ==
        "SELECT /* comment */ ... FROM `b`"
    )


def test_select_comment_show_columns(settings):
    assert (
        sql_fingerprint("SELECT /* comment */ `f1`, `f2` FROM `b`", hide_columns=False) ==
        "SELECT /* comment */ `f1`, `f2` FROM `b`"
    )


def test_select_join():
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a INNER JOIN b ON (a.b_id = b.id) WHERE a.f2 = 1') ==
        'SELECT ... FROM a INNER JOIN b ON (a.b_id = b.id) WHERE a.f2 = #'
    )


def test_select_join_show_columns(settings):
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a INNER JOIN b ON (a.b_id = b.id) WHERE a.f2 = 1', hide_columns=False) ==
        'SELECT f1, f2 FROM a INNER JOIN b ON (a.b_id = b.id) WHERE a.f2 = #'
    )


def test_select_order_by():
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a ORDER BY f3') ==
        'SELECT ... FROM a ORDER BY f3'
    )


def test_select_order_by_show_columns(settings):
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a ORDER BY f3', hide_columns=False) ==
        'SELECT f1, f2 FROM a ORDER BY f3'
    )


def test_select_order_by_multiple():
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a ORDER BY f3, f4') ==
        'SELECT ... FROM a ORDER BY f3, f4'
    )


def test_select_group_by():
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a GROUP BY f1') ==
        'SELECT ... FROM a GROUP BY f1'
    )


def test_select_group_by_show_columns(settings):
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a GROUP BY f1', hide_columns=False) ==
        'SELECT f1, f2 FROM a GROUP BY f1'
    )


def test_select_group_by_multiple():
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a GROUP BY f1, f2') ==
        'SELECT ... FROM a GROUP BY f1, f2'
    )


def test_select_group_by_having():
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a GROUP BY f1 HAVING f1 > 21') ==
        'SELECT ... FROM a GROUP BY f1 HAVING f1 > #'
    )


def test_select_group_by_having_show_columns(settings):
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a GROUP BY f1 HAVING f1 > 21', hide_columns=False) ==
        'SELECT f1, f2 FROM a GROUP BY f1 HAVING f1 > #'
    )


def test_select_group_by_having_multiple():
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a GROUP BY f1 HAVING f1 > 21, f2 < 42') ==
        'SELECT ... FROM a GROUP BY f1 HAVING f1 > #, f2 < #'
    )


def test_insert():
    assert (
        sql_fingerprint("INSERT INTO `table` (`f1`, `f2`) VALUES ('v1', 2)") ==
        "INSERT INTO `table` (...) VALUES (...)"
    )


def test_insert_show_columns(settings):
    assert (
        sql_fingerprint("INSERT INTO `table` (`f1`, `f2`) VALUES ('v1', 2)", hide_columns=False) ==
        "INSERT INTO `table` (`f1`, `f2`) VALUES (#, #)"
    )


def test_update():
    assert (
        sql_fingerprint("UPDATE `table` SET `foo` = 'bar' WHERE `table`.`id` = 1") ==
        "UPDATE `table` SET ... WHERE `table`.`id` = #"
    )


def test_declare_cursor():
    assert (
        sql_fingerprint('DECLARE "_django_curs_140239496394496_1300" NO SCROLL CURSOR WITHOUT') ==
        'DECLARE "_django_curs_#" NO SCROLL CURSOR WITHOUT'
    )


def test_savepoint():
    assert (
        sql_fingerprint("SAVEPOINT `s140323809662784_x54`") ==
        "SAVEPOINT `#`"
    )


def test_rollback_to_savepoint():
    assert (
        sql_fingerprint("ROLLBACK TO SAVEPOINT `s140323809662784_x54`") ==
        "ROLLBACK TO SAVEPOINT `#`"
    )


def test_release_savepoint():
    assert (
        sql_fingerprint("RELEASE SAVEPOINT `s140699855320896_x17`") ==
        "RELEASE SAVEPOINT `#`"
    )
