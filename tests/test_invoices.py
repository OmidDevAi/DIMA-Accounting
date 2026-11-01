# -*- coding: utf-8 -*-
"""Invoice history, filters and the full "undo" performed on delete."""

import pytest

from modules.invoices import InvoiceModule
from modules.modian import ModianModule
from modules.purchase import PurchaseModule
from modules.sales import SalesModule


def _sale_item(product):
    return {"product_id": product["id"], "qty_num": 1, "qty_box": 0,
            "units_per_box": 12, "price": 12000, "price_tier": 1}


def _stock(db, product):
    return db.fetch_one("SELECT stock_qty FROM products WHERE id = ?;", (product["id"],))["stock_qty"]


def test_delete_sale_restores_stock_cash_and_journal(db, admin, product):
    invoice_id, _, _ = SalesModule().create_sale_invoice(
        None, admin["id"], admin["box_id"], "cash", [_sale_item(product)]
    )
    assert _stock(db, product) == 99

    InvoiceModule().delete_invoice(invoice_id)

    assert _stock(db, product) == 100
    assert db.fetch_one("SELECT COUNT(*) AS c FROM invoices;")["c"] == 0
    assert db.fetch_one("SELECT COUNT(*) AS c FROM invoice_items;")["c"] == 0
    assert db.fetch_one(
        "SELECT COUNT(*) AS c FROM treasury_transactions WHERE invoice_id = ?;", (invoice_id,)
    )["c"] == 0
    assert db.fetch_one(
        "SELECT COUNT(*) AS c FROM journal_entries WHERE source_type = 'sale' AND source_id = ?;",
        (invoice_id,),
    )["c"] == 0


def test_delete_credit_sale_reverses_customer_balance(db, admin, product, party):
    invoice_id, _, total = SalesModule().create_sale_invoice(
        party["id"], admin["id"], admin["box_id"], "credit", [_sale_item(product)]
    )
    assert db.fetch_one("SELECT balance FROM parties WHERE id = ?;", (party["id"],))["balance"] == pytest.approx(total)

    InvoiceModule().delete_invoice(invoice_id)

    assert db.fetch_one("SELECT balance FROM parties WHERE id = ?;", (party["id"],))["balance"] == pytest.approx(0)


def test_delete_purchase_removes_gift_stock(db, admin, product):
    PurchaseModule().create_purchase_invoice(
        None, admin["id"], admin["box_id"], "cash",
        [{"product_id": product["id"], "qty_num": 0, "qty_box": 1,
          "units_per_box": 12, "price": 9000, "gift_qty": 3}],
    )
    assert _stock(db, product) == 115

    invoice_id = db.fetch_one("SELECT id FROM invoices;")["id"]
    InvoiceModule().delete_invoice(invoice_id)

    assert _stock(db, product) == 100


def test_invoice_history_filters(db, admin, product):
    db.execute("INSERT INTO cash_boxes (name, is_active) VALUES ('صندوق دوم', 1);")
    second_box_id = db.fetch_one("SELECT id FROM cash_boxes WHERE name = 'صندوق دوم';")["id"]

    SalesModule().create_sale_invoice(None, admin["id"], admin["box_id"], "cash", [_sale_item(product)])
    PurchaseModule().create_purchase_invoice(None, admin["id"], second_box_id, "cash",
                                             [{"product_id": product["id"], "qty_num": 1,
                                               "qty_box": 0, "units_per_box": 12, "price": 9000}])

    module = InvoiceModule()
    assert len(module.get_all_invoices()) == 2
    assert len(module.get_all_invoices(invoice_type="sale")) == 1
    assert len(module.get_all_invoices(box_id=second_box_id)) == 1
    assert module.get_all_invoices(invoice_type="purchase")[0]["box_id"] == second_box_id


def test_delete_missing_invoice_raises(db):
    with pytest.raises(ValueError):
        InvoiceModule().delete_invoice(999)


@pytest.mark.xfail(
    reason="known bug: deleting an invoice also deletes its prepared Modian record via ON DELETE CASCADE",
    strict=False,
)
def test_modian_record_survives_invoice_deletion(db, admin, product):
    invoice_id, _, _ = SalesModule().create_sale_invoice(
        None, admin["id"], admin["box_id"], "cash", [_sale_item(product)]
    )
    ModianModule().save_as_ready(invoice_id)

    InvoiceModule().delete_invoice(invoice_id)

    assert db.fetch_one(
        "SELECT COUNT(*) AS c FROM modian_invoices WHERE invoice_id = ?;", (invoice_id,)
    )["c"] == 1
