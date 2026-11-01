# -*- coding: utf-8 -*-
"""Cash-box transactions and their ledger effects."""

import pytest

from modules.treasury import TreasuryModule


def test_box_balance_is_receipts_minus_payments(db, admin):
    treasury = TreasuryModule()
    treasury.register_transaction("receive", 1000, admin["box_id"], admin["id"], skip_accounting=True)
    treasury.register_transaction("pay", 400, admin["box_id"], admin["id"], skip_accounting=True)

    assert treasury.get_box_balance(admin["box_id"]) == pytest.approx(600)


def test_balance_is_isolated_per_box(db, admin):
    second_box_id = db.execute("INSERT INTO cash_boxes (name, is_active) VALUES ('صندوق دوم', 1);")
    treasury = TreasuryModule()
    treasury.register_transaction("receive", 1000, admin["box_id"], admin["id"], skip_accounting=True)
    treasury.register_transaction("receive", 250, second_box_id, admin["id"], skip_accounting=True)

    assert treasury.get_box_balance(admin["box_id"]) == pytest.approx(1000)
    assert treasury.get_box_balance(second_box_id) == pytest.approx(250)


def test_customer_receipt_reduces_party_balance(db, admin, party):
    db.execute("UPDATE parties SET balance = 800000 WHERE id = ?;", (party["id"],))

    TreasuryModule().register_transaction(
        "receive", 300000, admin["box_id"], admin["id"],
        party_id=party["id"], skip_accounting=True,
    )

    balance = db.fetch_one("SELECT balance FROM parties WHERE id = ?;", (party["id"],))["balance"]
    assert balance == pytest.approx(500000)


def test_supplier_payment_moves_party_balance_toward_zero(db, admin):
    supplier_id = db.execute(
        "INSERT INTO parties (name, type, phone, balance) VALUES ('تامین‌کننده', 'supplier', '', -900000);"
    )

    TreasuryModule().register_transaction(
        "pay", 400000, admin["box_id"], admin["id"],
        party_id=supplier_id, skip_accounting=True,
    )

    balance = db.fetch_one("SELECT balance FROM parties WHERE id = ?;", (supplier_id,))["balance"]
    assert balance == pytest.approx(-500000)


def test_transaction_posts_journal_entry_unless_skipped(db, admin):
    treasury = TreasuryModule()
    treasury.register_transaction("receive", 1500, admin["box_id"], admin["id"])
    treasury.register_transaction("pay", 500, admin["box_id"], admin["id"], skip_accounting=True)

    entries = db.fetch_all("SELECT * FROM journal_entries WHERE source_type = 'treasury';")
    assert len(entries) == 1

    lines = db.fetch_all(
        "SELECT * FROM journal_entry_lines WHERE entry_id = ?;", (entries[0]["id"],)
    )
    assert sum(line["debit"] for line in lines) == pytest.approx(1500)
    assert sum(line["credit"] for line in lines) == pytest.approx(1500)


def test_transactions_are_filtered_by_box(db, admin):
    second_box_id = db.execute("INSERT INTO cash_boxes (name, is_active) VALUES ('صندوق دوم', 1);")
    treasury = TreasuryModule()
    treasury.register_transaction("receive", 100, admin["box_id"], admin["id"], skip_accounting=True)
    treasury.register_transaction("pay", 200, second_box_id, admin["id"], skip_accounting=True)

    assert len(treasury.get_transactions()) == 2
    assert len(treasury.get_transactions(box_id=second_box_id)) == 1
