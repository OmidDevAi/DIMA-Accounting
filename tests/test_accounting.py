# -*- coding: utf-8 -*-
"""Double-entry engine: balance rules, reports and automatic postings."""

import datetime

import pytest

from modules.accounting import AccountingModule
from modules.sales import SalesModule

TODAY = datetime.date.today().strftime("%Y%m%d")


def _ids(db):
    rows = db.fetch_all("SELECT id, code FROM accounts;")
    return {row["code"]: row["id"] for row in rows}


def test_balanced_entry_is_persisted(db, admin):
    accounts = _ids(db)
    accounting = AccountingModule()

    entry_id, number = accounting.create_journal_entry(
        "سند تست",
        [
            {"account_id": accounts["1000"], "debit": 1000, "credit": 0},
            {"account_id": accounts["4000"], "debit": 0, "credit": 1000},
        ],
        admin["id"],
    )

    assert number == f"JRN-{TODAY}-0001"
    lines = db.fetch_all(
        "SELECT * FROM journal_entry_lines WHERE entry_id = ?;", (entry_id,)
    )
    assert len(lines) == 2
    assert sum(line["debit"] for line in lines) == pytest.approx(sum(line["credit"] for line in lines))


def test_unbalanced_entry_is_rejected(db, admin):
    accounts = _ids(db)
    with pytest.raises(ValueError, match="نامتوازن"):
        AccountingModule().create_journal_entry(
            "سند نامتوازن",
            [
                {"account_id": accounts["1000"], "debit": 1000, "credit": 0},
                {"account_id": accounts["4000"], "debit": 0, "credit": 900},
            ],
            admin["id"],
        )
    assert db.fetch_one("SELECT COUNT(*) AS c FROM journal_entries;")["c"] == 0


def test_empty_entry_is_rejected(db, admin):
    with pytest.raises(ValueError, match="خالی"):
        AccountingModule().create_journal_entry("خالی", [], admin["id"])


def test_trial_balance_is_balanced(db, admin):
    accounts = _ids(db)
    accounting = AccountingModule()
    accounting.create_journal_entry(
        "خرید نقدی",
        [
            {"account_id": accounts["1000"], "debit": 500, "credit": 0},
            {"account_id": accounts["4000"], "debit": 0, "credit": 500},
        ],
        admin["id"],
    )
    accounting.create_journal_entry(
        "هزینه",
        [
            {"account_id": accounts["5000"], "debit": 200, "credit": 0},
            {"account_id": accounts["1000"], "debit": 0, "credit": 200},
        ],
        admin["id"],
    )

    rows = accounting.get_trial_balance()
    assert sum(row["total_debit"] for row in rows) == pytest.approx(700)
    assert sum(row["total_credit"] for row in rows) == pytest.approx(700)


def test_profit_and_loss_report(db, admin):
    accounts = _ids(db)
    accounting = AccountingModule()
    accounting.create_journal_entry(
        "درآمد",
        [
            {"account_id": accounts["1000"], "debit": 1000, "credit": 0},
            {"account_id": accounts["4000"], "debit": 0, "credit": 1000},
        ],
        admin["id"],
    )
    accounting.create_journal_entry(
        "هزینه",
        [
            {"account_id": accounts["5000"], "debit": 400, "credit": 0},
            {"account_id": accounts["1100"], "debit": 0, "credit": 400},
        ],
        admin["id"],
    )

    report = accounting.get_profit_and_loss("20000101", "20991231")
    assert report["total_revenue"] == pytest.approx(1000)
    assert report["total_expense"] == pytest.approx(400)
    assert report["net_profit"] == pytest.approx(600)


def test_balance_sheet_totals(db, admin):
    accounts = _ids(db)
    accounting = AccountingModule()
    accounting.create_journal_entry(
        "سرمایه",
        [
            {"account_id": accounts["1000"], "debit": 1000, "credit": 0},
            {"account_id": accounts["3000"], "debit": 0, "credit": 1000},
        ],
        admin["id"],
    )

    sheet = accounting.get_balance_sheet()
    assert sheet["total_assets"] == pytest.approx(1000)
    assert sheet["total_equity"] == pytest.approx(1000)
    assert sheet["total_liabilities"] == pytest.approx(0)


def test_general_ledger_running_balance(db, admin):
    accounts = _ids(db)
    accounting = AccountingModule()
    accounting.create_journal_entry(
        "واریز",
        [
            {"account_id": accounts["1000"], "debit": 1000, "credit": 0},
            {"account_id": accounts["3000"], "debit": 0, "credit": 1000},
        ],
        admin["id"],
    )
    accounting.create_journal_entry(
        "برداشت",
        [
            {"account_id": accounts["3000"], "debit": 400, "credit": 0},
            {"account_id": accounts["1000"], "debit": 0, "credit": 400},
        ],
        admin["id"],
    )

    ledger = accounting.get_general_ledger(accounts["1000"])
    assert [row["balance"] for row in ledger] == [1000, 600]


@pytest.mark.xfail(
    reason="known bug: entry numbers are counted for today only, so two backdated entries collide on the UNIQUE number",
    strict=False,
)
def test_backdated_entries_get_unique_numbers(db, admin):
    accounts = _ids(db)
    accounting = AccountingModule()
    lines = [
        {"account_id": accounts["1000"], "debit": 100, "credit": 0},
        {"account_id": accounts["3000"], "debit": 0, "credit": 100},
    ]

    _, first = accounting.create_journal_entry("سند اول", lines, admin["id"], date="20260101")
    _, second = accounting.create_journal_entry("سند دوم", lines, admin["id"], date="20260102")

    assert first != second


def test_auto_posted_sale_debits_cash_and_credits_revenue(db, admin, product):
    invoice_id, number, total = SalesModule().create_sale_invoice(
        None, admin["id"], admin["box_id"], "cash",
        [{"product_id": product["id"], "qty_num": 1, "qty_box": 0,
          "units_per_box": 12, "price": 12000, "price_tier": 1}],
    )

    accounting = AccountingModule()
    lines = db.fetch_all(
        """SELECT jel.* FROM journal_entry_lines jel
           JOIN journal_entries je ON je.id = jel.entry_id
           WHERE je.source_type = 'sale' AND je.source_id = ?;""",
        (invoice_id,),
    )
    by_account = {line["account_id"]: line for line in lines}

    cash_id = accounting.get_account_mapping("cash")
    revenue_id = accounting.get_account_mapping("sales_revenue")
    assert by_account[cash_id]["debit"] == pytest.approx(total)
    assert by_account[revenue_id]["credit"] == pytest.approx(total)


def test_auto_posting_is_skipped_when_mapping_is_missing(db, admin, product):
    db.execute("DELETE FROM account_mappings;")
    invoice_id, _, total = SalesModule().create_sale_invoice(
        None, admin["id"], admin["box_id"], "cash",
        [{"product_id": product["id"], "qty_num": 1, "qty_box": 0,
          "units_per_box": 12, "price": 12000, "price_tier": 1}],
    )

    assert total == pytest.approx(12000)
    assert db.fetch_one(
        "SELECT COUNT(*) AS c FROM journal_entries WHERE source_type = 'sale';"
    )["c"] == 0


def test_account_mapping_can_be_changed(db, admin):
    accounts = _ids(db)
    accounting = AccountingModule()
    accounting.set_account_mapping("cash", accounts["1100"])
    assert accounting.get_account_mapping("cash") == accounts["1100"]


@pytest.mark.xfail(
    reason="known gap: sales never post cost of goods sold, so the inventory account is never credited",
    strict=False,
)
def test_sale_posts_cost_of_goods_sold(db, admin, product):
    invoice_id, _, total = SalesModule().create_sale_invoice(
        None, admin["id"], admin["box_id"], "cash",
        [{"product_id": product["id"], "qty_num": 2, "qty_box": 0,
          "units_per_box": 12, "price": 12000, "price_tier": 1}],
    )

    inventory_id = AccountingModule().get_account_mapping("inventory")
    line = db.fetch_one(
        """SELECT jel.* FROM journal_entry_lines jel
           JOIN journal_entries je ON je.id = jel.entry_id
           WHERE je.source_type = 'sale' AND je.source_id = ? AND jel.account_id = ?;""",
        (invoice_id, inventory_id),
    )
    assert line is not None
    assert line["credit"] == pytest.approx(2 * product["buy_price"])


@pytest.mark.xfail(
    reason="known gap: collected VAT is posted to the sales revenue account instead of the VAT payable account",
    strict=False,
)
def test_sale_posts_vat_to_payable_account(db, admin, product):
    invoice_id, _, total = SalesModule().create_sale_invoice(
        None, admin["id"], admin["box_id"], "cash",
        [{"product_id": product["id"], "qty_num": 1, "qty_box": 0, "units_per_box": 12,
          "price": 100000, "price_tier": 1, "has_tax": True, "tax_percent": 9}],
    )

    vat_id = AccountingModule().get_account_mapping("vat_payable")
    line = db.fetch_one(
        """SELECT jel.* FROM journal_entry_lines jel
           JOIN journal_entries je ON je.id = jel.entry_id
           WHERE je.source_type = 'sale' AND je.source_id = ? AND jel.account_id = ?;""",
        (invoice_id, vat_id),
    )
    assert line is not None
    assert line["credit"] == pytest.approx(9000)
