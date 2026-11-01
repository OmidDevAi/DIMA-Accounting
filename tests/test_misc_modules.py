# -*- coding: utf-8 -*-
"""Customers, settings, SMS provider layer and Modian data preparation."""

import pytest

from modules.app_settings import AppSettingsModule
from modules.customers import CustomerModule
from modules.modian import ModianModule
from modules.scanner_settings import ScannerSettingsModule
from modules.sales import SalesModule
from modules.sms import SMSModule


# ---------------------------------------------------------------- customers
def test_get_or_create_customer_by_phone(db):
    customers = CustomerModule()
    first_id = customers.get_or_create_customer("09121111111", "علی")

    assert customers.get_or_create_customer("09121111111", "نام دیگر") == first_id
    assert customers.get_or_create_customer("09129999999") is None
    assert customers.find_by_phone("09121111111")["name"] == "علی"


def test_customer_search_matches_name_and_phone(db):
    customers = CustomerModule()
    customers.create_customer("مریم", "09350000000")
    customers.create_customer("رضا", "09120000001")

    assert [row["name"] for row in customers.search_customers("مریم")] == ["مریم"]
    assert [row["name"] for row in customers.search_customers("0912")] == ["رضا"]


def test_inactive_customers_have_no_recent_invoice(db, admin, product):
    customers = CustomerModule()
    active_id = customers.create_customer("خریدار", "09120000002")
    customers.create_customer("بدون خرید", "09120000003")

    SalesModule().create_sale_invoice(
        active_id, admin["id"], admin["box_id"], "credit",
        [{"product_id": product["id"], "qty_num": 1, "qty_box": 0,
          "units_per_box": 12, "price": 12000, "price_tier": 1}],
    )

    inactive = customers.find_inactive_customers("20000101", "20991231")
    assert [row["name"] for row in inactive] == ["بدون خرید"]


def test_customer_invoice_history_is_scoped_by_date(db):
    customers = CustomerModule()
    customer_id = customers.create_customer("قدیمی", "09120000004")
    assert customers.get_customer_invoices(customer_id) == []


# ---------------------------------------------------------------- settings
def test_app_settings_default_and_persisted_language(db):
    settings = AppSettingsModule()
    assert settings.get_language() == "fa"

    settings.save_language("en")
    assert settings.get_language() == "en"
    settings.save_language("de")
    assert settings.get_language() == "de"
    assert db.fetch_one("SELECT COUNT(*) AS c FROM app_settings;")["c"] == 1


def test_scanner_settings_roundtrip(db):
    scanner = ScannerSettingsModule()
    assert scanner.get_settings() == {"mode": "usb", "port": "", "baud_rate": 9600}

    scanner.save_settings("serial", "COM3", 115200)
    assert scanner.get_settings() == {"mode": "serial", "port": "COM3", "baud_rate": 115200}


# ---------------------------------------------------------------- sms
def test_sms_defaults(db):
    settings = SMSModule().get_settings()
    assert settings["provider"] == "generic"
    assert settings["api_key"] == ""


def test_sms_without_configuration_is_logged_not_sent(db):
    sms = SMSModule()
    status = sms.send_sms("09120000000", "سلام", user_id=1)

    assert status == "not_configured"
    log = db.fetch_one("SELECT * FROM sms_log;")
    assert log["status"] == "not_configured"
    assert log["phone"] == "09120000000"


def test_sms_settings_roundtrip_and_bulk_skips_empty_phone(db):
    sms = SMSModule()
    sms.save_settings("kavenegar", "https://api.kavenegar.com", "demo-key", "1000", "POST", "")

    settings = sms.get_settings()
    assert settings["provider"] == "kavenegar"
    assert settings["api_key"] == "demo-key"
    assert db.fetch_one("SELECT COUNT(*) AS c FROM sms_settings;")["c"] == 1

    results = sms.send_bulk([{"name": "بدون شماره", "phone": ""}], "متن", user_id=1)
    assert results == []


# ---------------------------------------------------------------- modian
def _make_sale(db, admin, product, **item_overrides):
    item = {"product_id": product["id"], "qty_num": 1, "qty_box": 0,
            "units_per_box": 12, "price": 12000, "price_tier": 1}
    item.update(item_overrides)
    return SalesModule().create_sale_invoice(
        None, admin["id"], admin["box_id"], "cash", [item]
    )


def test_modian_payload_contains_invoice_and_items(db, admin, product):
    invoice_id, number, total = _make_sale(db, admin, product)
    payload = ModianModule().prepare_invoice_payload(invoice_id)

    assert payload["invoice_number"] == number
    assert payload["total_amount"] == pytest.approx(total)
    assert payload["buyer"]["name"] == "مصرف‌کننده نهایی"
    assert len(payload["items"]) == 1
    assert payload["items"][0]["product_code"] == product["code"]


def test_modian_ready_status_and_pending_list(db, admin, product):
    invoice_id, _, _ = _make_sale(db, admin, product)
    modian = ModianModule()

    assert len(modian.get_pending_invoices()) == 1
    modian.save_as_ready(invoice_id, tax_id="T-1", uid="U-1")

    record = db.fetch_one("SELECT * FROM modian_invoices WHERE invoice_id = ?;", (invoice_id,))
    assert record["status"] == "ready"
    assert modian.get_pending_invoices() == []

    modian.save_as_ready(invoice_id, tax_id="T-2")
    assert db.fetch_one("SELECT COUNT(*) AS c FROM modian_invoices;")["c"] == 1


def test_modian_live_submission_is_not_implemented(db, admin, product):
    invoice_id, _, _ = _make_sale(db, admin, product)
    with pytest.raises(NotImplementedError):
        ModianModule().send_to_modian(invoice_id)


def test_modian_quantity_uses_base_units(db, admin, product):
    invoice_id, _, _ = _make_sale(db, admin, product, qty_num=3, qty_box=2)
    payload = ModianModule().prepare_invoice_payload(invoice_id)

    assert payload["items"][0]["quantity"] == 27
