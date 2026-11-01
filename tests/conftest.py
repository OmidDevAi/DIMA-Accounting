# -*- coding: utf-8 -*-
"""Shared fixtures for the DIMA Accounting test-suite.

Every test gets a brand-new SQLite file in ``tmp_path`` so the developer's
real ``dima_accounting.db`` is never touched.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.auth import AuthManager  # noqa: E402
from core.db_manager import DBManager  # noqa: E402


@pytest.fixture
def db(tmp_path):
    DBManager._instance = None
    AuthManager._instance = None
    manager = DBManager(db_path=str(tmp_path / "test.db"))
    yield manager
    manager.close()
    DBManager._instance = None
    AuthManager._instance = None


@pytest.fixture
def admin(db):
    user = AuthManager.instance().login("admin", "admin123")
    assert user is not None, "seeded admin login must work"
    return user


@pytest.fixture
def cashier(db):
    AuthManager.create_user("cashier1", "pass1234", "صندوق‌دار تست", "cashier", 1)
    user = AuthManager.instance().login("cashier1", "pass1234")
    assert user is not None
    return user


@pytest.fixture
def party(db):
    from modules.customers import CustomerModule

    customer_id = CustomerModule().create_customer("مشتری تست", "09120000000")
    return db.fetch_one("SELECT * FROM parties WHERE id = ?;", (customer_id,))


@pytest.fixture
def product(db):
    from modules.inventory import InventoryModule

    inventory = InventoryModule()
    product_id = inventory.add_product(
        "6260000000001", "P-001", "شیر پرچرب", "عدد", 12,
        9000, 12000, 13000, 14000, 15000, 5,
    )
    db.execute("UPDATE products SET stock_qty = 100 WHERE id = ?;", (product_id,))
    return db.fetch_one("SELECT * FROM products WHERE id = ?;", (product_id,))
