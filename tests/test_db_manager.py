# -*- coding: utf-8 -*-
"""Database bootstrap, seeding and password hashing."""

import sqlite3

import pytest

from core.db_manager import DBManager

EXPECTED_TABLES = {
    "cash_boxes",
    "users",
    "product_categories",
    "price_tier_labels",
    "products",
    "parties",
    "invoices",
    "invoice_items",
    "treasury_transactions",
    "accounts",
    "journal_entries",
    "journal_entry_lines",
    "account_mappings",
    "checks",
    "modian_invoices",
    "modian_settings",
    "scanner_settings",
    "sms_settings",
    "sms_log",
    "app_settings",
}


def test_database_file_is_created(db):
    assert (db.db_path).endswith("test.db")
    assert db.fetch_one("SELECT 1 AS ok;")["ok"] == 1


def test_schema_contains_all_expected_tables(db):
    tables = {
        row["name"]
        for row in db.fetch_all("SELECT name FROM sqlite_master WHERE type = 'table';")
    }
    assert EXPECTED_TABLES <= tables


def test_seed_creates_admin_box_accounts_and_categories(db):
    users = db.fetch_all("SELECT * FROM users;")
    assert len(users) == 1
    assert users[0]["username"] == "admin"
    assert users[0]["role"] == "admin"

    boxes = db.fetch_all("SELECT * FROM cash_boxes;")
    assert len(boxes) == 1

    assert db.fetch_one("SELECT COUNT(*) AS c FROM accounts;")["c"] == 10
    assert db.fetch_one("SELECT COUNT(*) AS c FROM price_tier_labels;")["c"] == 4
    assert db.fetch_one("SELECT COUNT(*) AS c FROM account_mappings;")["c"] == 9
    assert db.fetch_one("SELECT COUNT(*) AS c FROM product_categories;")["c"] > 0


def test_seed_is_idempotent(db):
    counts_before = {
        table: db.fetch_one(f"SELECT COUNT(*) AS c FROM {table};")["c"]
        for table in ("users", "cash_boxes", "accounts", "product_categories")
    }

    path = db.db_path
    db.close()
    DBManager._instance = None
    reopened = DBManager(db_path=path)

    counts_after = {
        table: reopened.fetch_one(f"SELECT COUNT(*) AS c FROM {table};")["c"]
        for table in ("users", "cash_boxes", "accounts", "product_categories")
    }
    assert counts_after == counts_before


def test_instance_returns_the_same_singleton(db):
    assert DBManager.instance() is db


def test_foreign_keys_are_enforced(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO products (code, name, group_main_id) VALUES ('X-1', 'نامعتبر', 999);"
        )


def test_legacy_modian_table_is_migrated_to_set_null(db):
    db.execute(
        """INSERT INTO invoices
           (invoice_number, invoice_type, date, user_id, box_id, payment_type)
           VALUES ('SAL-LEGACY-0001', 'sale', '20260101', 1, 1, 'cash');"""
    )
    invoice_id = db.fetch_one(
        "SELECT id FROM invoices WHERE invoice_number = 'SAL-LEGACY-0001';"
    )["id"]

    path = db.db_path
    db.close()
    DBManager._instance = None

    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(
        f"""
        DROP TABLE modian_invoices;
        CREATE TABLE modian_invoices (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id      INTEGER NOT NULL UNIQUE,
            tax_id          TEXT,
            uid             TEXT,
            status          TEXT NOT NULL DEFAULT 'not_prepared',
            payload_json    TEXT,
            prepared_at     TEXT,
            sent_at         TEXT,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
        );
        INSERT INTO modian_invoices (invoice_id, status)
        VALUES ({invoice_id}, 'ready');
        """
    )
    conn.commit()
    conn.close()

    migrated = DBManager(db_path=path)
    fk = next(
        row for row in migrated.fetch_all("PRAGMA foreign_key_list(modian_invoices);")
        if row["from"] == "invoice_id"
    )
    assert fk["on_delete"] == "SET NULL"

    migrated.execute("DELETE FROM invoices WHERE id = ?;", (invoice_id,))
    record = migrated.fetch_one("SELECT * FROM modian_invoices;")
    assert record is not None
    assert record["invoice_id"] is None
    migrated.close()


def test_hash_password_is_salted_and_verifiable():
    first_hash, first_salt = DBManager.hash_password("secret")
    second_hash, second_salt = DBManager.hash_password("secret")

    assert len(first_hash) == 64
    assert len(first_salt) == 32
    assert first_hash != second_hash  # different random salt

    rehash, _ = DBManager.hash_password("secret", bytes.fromhex(first_salt))
    assert rehash == first_hash

    wrong, _ = DBManager.hash_password("Secret", bytes.fromhex(first_salt))
    assert wrong != first_hash
