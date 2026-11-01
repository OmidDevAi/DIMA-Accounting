# -*- coding: utf-8 -*-
"""Authentication, roles and cash-box isolation rules."""

import sqlite3

import pytest

from core.auth import AuthManager


def test_seeded_admin_can_login(db):
    user = AuthManager.instance().login("admin", "admin123")
    assert user is not None
    assert user["role"] == "admin"
    assert user["box_id"] == 1


def test_wrong_password_is_rejected(db):
    assert AuthManager.instance().login("admin", "wrong-password") is None


def test_unknown_user_is_rejected(db):
    assert AuthManager.instance().login("nobody", "admin123") is None


def test_inactive_user_cannot_login(db):
    AuthManager.create_user("inactive1", "pass1234", "کاربر غیرفعال", "cashier", 1)
    user_id = db.fetch_one("SELECT id FROM users WHERE username = 'inactive1';")["id"]
    AuthManager.set_user_active(user_id, False)

    assert AuthManager.instance().login("inactive1", "pass1234") is None


def test_logout_clears_session(db, admin):
    auth = AuthManager.instance()
    assert auth.is_authenticated()
    auth.logout()
    assert not auth.is_authenticated()
    assert auth.get_accessible_box_id() == -1


def test_permissions_for_admin_and_cashier(db, admin):
    auth = AuthManager.instance()
    assert auth.is_admin()
    assert not auth.is_accountant()
    assert auth.can_manage_products()
    assert auth.can_send_bulk_sms()
    assert auth.can_search_inactive_customers()
    assert auth.get_accessible_box_id() is None

    AuthManager.create_user("cashier1", "pass1234", "صندوق‌دار", "cashier", 1)
    auth.logout()
    auth.login("cashier1", "pass1234")
    assert not auth.is_admin()
    assert not auth.can_manage_products()
    assert not auth.can_send_bulk_sms()
    assert auth.can_search_inactive_customers()
    assert auth.get_accessible_box_id() == 1


def test_accountant_permissions(db):
    AuthManager.create_user("acc1", "pass1234", "حسابدار", "accountant", 1)
    auth = AuthManager.instance()
    auth.login("acc1", "pass1234")
    assert auth.is_accountant()
    assert auth.can_manage_products()
    assert auth.can_send_bulk_sms()
    assert not auth.can_search_inactive_customers()


def test_duplicate_username_is_rejected(db):
    AuthManager.create_user("dup", "pass1234", "اول", "cashier", 1)
    with pytest.raises(sqlite3.IntegrityError):
        AuthManager.create_user("dup", "pass1234", "دوم", "cashier", 1)


def test_password_change_takes_effect(db):
    user_id = AuthManager.create_user("u1", "oldpass1", "کاربر", "cashier", 1)
    auth = AuthManager.instance()

    assert auth.login("u1", "oldpass1") is not None
    auth.logout()

    AuthManager.set_user_password(user_id, "newpass2")
    assert auth.login("u1", "oldpass1") is None
    assert auth.login("u1", "newpass2") is not None
