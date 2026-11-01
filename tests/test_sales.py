# -*- coding: utf-8 -*-
"""Sales invoice: stock, totals, treasury and ledger side effects."""

import datetime

import pytest

from modules.invoices import InvoiceModule
from modules.sales import SalesModule

TODAY = datetime.date.today().strftime("%Y%m%d")


def _item(product, **overrides):
    item = {
        "product_id": product["id"],
        "qty_num": 1,
        "qty_box": 0,
        "units_per_box": product["units_per_box"],
        "price": product["sell_price_1"],
        "price_tier": 1,
    }
    item.update(overrides)
    return item


def _stock(db, product):
    return db.fetch_one("SELECT stock_qty FROM products WHERE id = ?;", (product["id"],))["stock_qty"]


def test_cash_sale_updates_stock_treasury_and_journal(db, admin, product):
    invoice_id, number, total = SalesModule().create_sale_invoice(
        party_id=None, user_id=admin["id"], box_id=admin["box_id"],
        payment_type="cash", items=[_item(product, qty_num=2, qty_box=1)],
    )

    assert number.startswith(f"SAL-{TODAY}-")
    assert total == pytest.approx(14 * product["sell_price_1"])
    assert _stock(db, product) == 86

    treasury = db.fetch_all(
        "SELECT * FROM treasury_transactions WHERE invoice_id = ?;", (invoice_id,)
    )
    assert len(treasury) == 1
    assert treasury[0]["trans_type"] == "receive"
    assert treasury[0]["amount"] == pytest.approx(total)

    entry = db.fetch_one(
        "SELECT * FROM journal_entries WHERE source_type = 'sale' AND source_id = ?;",
        (invoice_id,),
    )
    assert entry is not None


def test_sale_totals_apply_line_discount_tax_invoice_discount_and_duty(db, admin, product):
    invoice_id, _, total = SalesModule().create_sale_invoice(
        party_id=None, user_id=admin["id"], box_id=admin["box_id"],
        payment_type="cash",
        items=[_item(product, price=100000, discount_amount=10, discount_type="percent",
                     has_tax=True, tax_percent=9)],
        invoice_discount=5000, invoice_discount_type="rial", duty_amount=2000,
    )

    invoice = db.fetch_one("SELECT * FROM invoices WHERE id = ?;", (invoice_id,))
    line = db.fetch_one("SELECT * FROM invoice_items WHERE invoice_id = ?;", (invoice_id,))

    assert invoice["subtotal_amount"] == pytest.approx(100000)
    assert invoice["tax_amount"] == pytest.approx(8100)
    assert invoice["total_amount"] == pytest.approx(105100)
    assert line["line_total"] == pytest.approx(98100)
    assert total == pytest.approx(105100)


def test_insufficient_stock_rolls_back_the_whole_invoice(db, admin, product):
    db.execute("UPDATE products SET stock_qty = 5 WHERE id = ?;", (product["id"],))

    with pytest.raises(ValueError, match="موجودی کافی"):
        SalesModule().create_sale_invoice(
            party_id=None, user_id=admin["id"], box_id=admin["box_id"],
            payment_type="cash", items=[_item(product, qty_num=10)],
        )

    assert db.fetch_one("SELECT COUNT(*) AS c FROM invoices;")["c"] == 0
    assert db.fetch_one("SELECT COUNT(*) AS c FROM invoice_items;")["c"] == 0
    assert _stock(db, product) == 5


def test_credit_sale_increases_receivable_and_skips_treasury(db, admin, product, party):
    invoice_id, _, total = SalesModule().create_sale_invoice(
        party_id=party["id"], user_id=admin["id"], box_id=admin["box_id"],
        payment_type="credit", items=[_item(product, price=500000)],
    )

    balance = db.fetch_one("SELECT balance FROM parties WHERE id = ?;", (party["id"],))["balance"]
    assert balance == pytest.approx(500000)
    assert db.fetch_one(
        "SELECT COUNT(*) AS c FROM treasury_transactions WHERE invoice_id = ?;", (invoice_id,)
    )["c"] == 0

    entry_line = db.fetch_one(
        """SELECT jel.* FROM journal_entry_lines jel
           JOIN journal_entries je ON je.id = jel.entry_id
           WHERE je.source_type = 'sale' AND je.source_id = ? AND jel.debit > 0;""",
        (invoice_id,),
    )
    assert entry_line is not None
    assert entry_line["debit"] == pytest.approx(total)


def test_sale_invoices_are_filtered_by_box(db, admin, product):
    db.execute("INSERT INTO cash_boxes (name, is_active) VALUES ('صندوق دوم', 1);")
    second_box_id = db.fetch_one("SELECT id FROM cash_boxes WHERE name = 'صندوق دوم';")["id"]

    sales = SalesModule()
    sales.create_sale_invoice(None, admin["id"], admin["box_id"], "cash", [_item(product)])
    sales.create_sale_invoice(None, admin["id"], second_box_id, "cash", [_item(product)])

    assert len(sales.get_sale_invoices()) == 2
    assert len(sales.get_sale_invoices(box_id=second_box_id)) == 1
    assert sales.get_sale_invoices(box_id=second_box_id)[0]["box_id"] == second_box_id


@pytest.mark.xfail(
    reason="known bug: invoice numbers use COUNT(*)+1, so deleting an invoice makes the next number collide",
    strict=False,
)
def test_invoice_numbering_survives_deleting_an_invoice(db, admin, product):
    sales = SalesModule()
    first_id, first_number, _ = sales.create_sale_invoice(
        None, admin["id"], admin["box_id"], "cash", [_item(product)]
    )
    _, second_number, _ = sales.create_sale_invoice(
        None, admin["id"], admin["box_id"], "cash", [_item(product)]
    )
    assert (first_number, second_number) == (f"SAL-{TODAY}-0001", f"SAL-{TODAY}-0002")

    InvoiceModule().delete_invoice(first_id)
    sales.create_sale_invoice(None, admin["id"], admin["box_id"], "cash", [_item(product)])


@pytest.mark.xfail(
    reason="known bug: an empty sale is accepted (a zero-amount invoice and treasury row are created)",
    strict=False,
)
def test_empty_invoice_is_rejected(db, admin):
    with pytest.raises(ValueError):
        SalesModule().create_sale_invoice(
            None, admin["id"], admin["box_id"], "cash", []
        )
    assert db.fetch_one("SELECT COUNT(*) AS c FROM invoices;")["c"] == 0
