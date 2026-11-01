# -*- coding: utf-8 -*-
"""Purchase invoice: stock increase, gift quantities and supplier balance."""

import datetime

import pytest

from modules.purchase import PurchaseModule

TODAY = datetime.date.today().strftime("%Y%m%d")


def _item(product, **overrides):
    item = {
        "product_id": product["id"],
        "qty_num": 1,
        "qty_box": 0,
        "units_per_box": product["units_per_box"],
        "price": product["buy_price"],
    }
    item.update(overrides)
    return item


def _stock(db, product):
    return db.fetch_one("SELECT stock_qty FROM products WHERE id = ?;", (product["id"],))["stock_qty"]


def test_cash_purchase_adds_stock_gift_and_updates_buy_price(db, admin, product):
    invoice_id, number, total = PurchaseModule().create_purchase_invoice(
        party_id=None, user_id=admin["id"], box_id=admin["box_id"],
        payment_type="cash",
        items=[_item(product, qty_num=0, qty_box=1, gift_qty=2, price=10000)],
    )

    assert number.startswith(f"PUR-{TODAY}-")
    assert total == pytest.approx(12 * 10000)
    assert _stock(db, product) == 100 + 12 + 2

    updated = db.fetch_one("SELECT buy_price FROM products WHERE id = ?;", (product["id"],))
    assert updated["buy_price"] == 10000

    treasury = db.fetch_all(
        "SELECT * FROM treasury_transactions WHERE invoice_id = ?;", (invoice_id,)
    )
    assert len(treasury) == 1
    assert treasury[0]["trans_type"] == "pay"


def test_purchase_totals_with_tax_and_discount(db, admin, product):
    invoice_id, _, total = PurchaseModule().create_purchase_invoice(
        party_id=None, user_id=admin["id"], box_id=admin["box_id"],
        payment_type="cash",
        items=[_item(product, price=100000, discount_amount=5, discount_type="percent",
                     has_tax=True, tax_percent=9)],
        duty_amount=1000,
    )

    invoice = db.fetch_one("SELECT * FROM invoices WHERE id = ?;", (invoice_id,))
    assert invoice["subtotal_amount"] == pytest.approx(100000)
    assert invoice["tax_amount"] == pytest.approx(8550)
    assert invoice["total_amount"] == pytest.approx(109550)
    assert total == pytest.approx(109550)


def test_credit_purchase_tracks_supplier_payable(db, admin, product):
    supplier_id = db.execute(
        "INSERT INTO parties (name, type, phone, balance) VALUES ('تامین‌کننده', 'supplier', '021000', 0);"
    )

    PurchaseModule().create_purchase_invoice(
        party_id=supplier_id, user_id=admin["id"], box_id=admin["box_id"],
        payment_type="credit",
        items=[_item(product, price=300000)],
    )

    balance = db.fetch_one("SELECT balance FROM parties WHERE id = ?;", (supplier_id,))["balance"]
    assert balance == pytest.approx(-300000)


def test_purchase_invoices_are_filtered_by_box(db, admin, product):
    db.execute("INSERT INTO cash_boxes (name, is_active) VALUES ('صندوق دوم', 1);")
    second_box_id = db.fetch_one("SELECT id FROM cash_boxes WHERE name = 'صندوق دوم';")["id"]

    purchases = PurchaseModule()
    purchases.create_purchase_invoice(None, admin["id"], admin["box_id"], "cash", [_item(product)])
    purchases.create_purchase_invoice(None, admin["id"], second_box_id, "cash", [_item(product)])

    assert len(purchases.get_purchase_invoices()) == 2
    assert len(purchases.get_purchase_invoices(box_id=second_box_id)) == 1
