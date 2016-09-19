# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django_perf_rec.sql import sql_fingerprint


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


def test_select_comment():
    assert (
        sql_fingerprint("SELECT /* comment */ `f1`, `f2` FROM `b`") ==
        "SELECT /* comment */ ... FROM `b`"
    )


def test_select_join():
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a INNER JOIN b ON (a.b_id = b.id) WHERE a.f2 = 1') ==
        'SELECT ... FROM a INNER JOIN b ON (a.b_id = b.id) WHERE a.f2 = #'
    )


def test_select_order_by():
    assert (
        sql_fingerprint('SELECT f1, f2 FROM a ORDER BY f3, f4') ==
        'SELECT ... FROM a ORDER BY ...'
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
