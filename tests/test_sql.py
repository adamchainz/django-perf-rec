from django_performance_recorder.sql import sql_fingerprint


def test_select():
    assert (
        sql_fingerprint("SELECT `f1`, `f2` FROM `b`") ==
        "SELECT ... FROM `b`"
    )


def test_select_where():
    assert (
        sql_fingerprint("SELECT DISTINCT `table`.`field` FROM `table` WHERE `table`.`id` = 1") ==
        "SELECT DISTINCT `table`.`field` FROM `table` WHERE `table`.`id` = #"
    )


def test_insert():
    assert (
        sql_fingerprint("INSERT INTO `table` (`f1`, `f2`) VALUES ('v1', 2)") ==
        "INSERT INTO `table` (...) VALUES (...)"
    )


def test_update():
    assert (
        sql_fingerprint("UPDATE `table` SET `foo` = 'bar' WHERE `table`.`id` = 1") ==
        "UPDATE `table` SET ... WHERE `table`.`id` = #"
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
