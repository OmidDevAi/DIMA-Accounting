# -*- coding: utf-8 -*-
"""Product catalogue, unit conversion and stock adjustments."""

import pytest

from modules.inventory import InventoryModule


@pytest.mark.parametrize(
    "qty_num, qty_box, units_per_box, expected",
    [
        (0, 0, 12, 0),
        (3, 0, 12, 3),
        (0, 2, 12, 24),
        (3, 2, 12, 27),
        (1.5, 0, 1, 1.5),
    ],
)
def test_convert_to_base_units(qty_num, qty_box, units_per_box, expected):
    assert InventoryModule.convert_to_base_units(qty_num, qty_box, units_per_box) == expected


def test_add_and_find_product_by_barcode(db):
    inventory = InventoryModule()
    product_id = inventory.add_product(
        "6261111111111", "P-100", "پنیر", "عدد", 6,
        50000, 65000, 70000, 72000, 75000, 3,
    )

    found = inventory.find_by_barcode("6261111111111")
    assert found is not None
    assert found["id"] == product_id
    assert found["name"] == "پنیر"
    assert found["units_per_box"] == 6


def test_search_products_matches_name_code_and_barcode(db):
    inventory = InventoryModule()
    inventory.add_product("111", "AA-1", "شیر کم‌چرب", "عدد", 1, 1, 2, 2, 2, 2, 0)
    inventory.add_product("222", "BB-2", "ماست", "عدد", 1, 1, 2, 2, 2, 2, 0)

    assert [row["code"] for row in inventory.search_products("شیر")] == ["AA-1"]
    assert [row["code"] for row in inventory.search_products("BB")] == ["BB-2"]
    assert [row["code"] for row in inventory.search_products("111")] == ["AA-1"]


def test_update_product_changes_only_given_fields(db, product):
    inventory = InventoryModule()
    inventory.update_product(product["id"], name="شیر بدون چربی", buy_price=9100)

    updated = db.fetch_one("SELECT * FROM products WHERE id = ?;", (product["id"],))
    assert updated["name"] == "شیر بدون چربی"
    assert updated["buy_price"] == 9100
    assert updated["sell_price_1"] == product["sell_price_1"]


def test_low_stock_uses_min_stock_threshold(db, product):
    inventory = InventoryModule()
    assert [row["id"] for row in inventory.get_low_stock_products()] == []

    db.execute("UPDATE products SET stock_qty = 5 WHERE id = ?;", (product["id"],))
    assert [row["id"] for row in inventory.get_low_stock_products()] == [product["id"]]


def test_adjust_stock_inside_transaction(db, product):
    inventory = InventoryModule()
    with db.transaction() as cur:
        inventory.adjust_stock(cur, product["id"], -10)
        inventory.adjust_stock(cur, product["id"], 4)

    stock = db.fetch_one("SELECT stock_qty FROM products WHERE id = ?;", (product["id"],))
    assert stock["stock_qty"] == 94


def test_price_tier_labels_are_editable(db):
    inventory = InventoryModule()
    labels = inventory.get_price_tier_labels()
    assert labels == {1: "قیمت نقدی", 2: "قیمت نسیه", 3: "قیمت قدیم", 4: "قیمت جدید"}

    inventory.update_price_tier_label(2, "قیمت عمده")
    assert inventory.get_price_tier_labels()[2] == "قیمت عمده"


def test_categories_are_seeded_with_subgroups(db):
    inventory = InventoryModule()
    main_groups = inventory.get_main_groups()
    assert {row["name"] for row in main_groups} >= {"لبنیات", "خواروبار", "نوشیدنی"}

    dairy = next(row for row in main_groups if row["name"] == "لبنیات")
    assert {row["name"] for row in inventory.get_sub_groups(dairy["id"])} == {
        "شیر و ماست", "پنیر", "بستنی",
    }

    new_id = inventory.add_category("خشکبار", dairy["id"])
    assert any(row["id"] == new_id for row in inventory.get_sub_groups(dairy["id"]))
