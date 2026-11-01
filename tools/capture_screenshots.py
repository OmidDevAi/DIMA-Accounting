# -*- coding: utf-8 -*-
"""Render every DIMA Accounting screen into PNG files for the README.

A throw-away demo database is created in the temp directory, so the
developer's real database is never touched. The application windows are
painted with ``WA_DontShowOnScreen``: they are laid out normally but never
appear on the desktop.

The script needs a Windows desktop session (Qt's offscreen plugin ships
without a font database, so text would not render there).

Usage:
    python tools/capture_screenshots.py
"""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt6.QtCore import Qt  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

from core.auth import AuthManager  # noqa: E402
from core.db_manager import DBManager  # noqa: E402
from core.i18n import set_language  # noqa: E402
from modules.checks import CheckModule  # noqa: E402
from modules.customers import CustomerModule  # noqa: E402
from modules.inventory import InventoryModule  # noqa: E402
from modules.modian import ModianModule  # noqa: E402
from modules.purchase import PurchaseModule  # noqa: E402
from modules.sales import SalesModule  # noqa: E402
from ui.login_window import LoginWindow  # noqa: E402
from ui.main_window import MainWindow  # noqa: E402

OUTPUT_DIR = ROOT / "docs" / "screenshots"
WINDOW_SIZE = (1280, 800)

PRODUCTS = [
    # barcode, code, name, unit, units_per_box, buy, s1, s2, s3, s4, min_stock, stock
    ("6260100000001", "LB-1001", "شیر پرچرب ۱ لیتری", "عدد", 12, 32000, 39000, 41000, 38000, 42000, 24, 186),
    ("6260100000002", "LB-1002", "ماست دبه‌ای ۲ کیلویی", "عدد", 6, 85000, 99000, 105000, 96000, 110000, 12, 64),
    ("6260100000003", "LB-1003", "پنیر سفید ۴۰۰ گرمی", "عدد", 12, 62000, 78000, 82000, 75000, 85000, 12, 9),
    ("6260200000001", "GR-2001", "برنج ایرانی هاشمی ۱۰ کیلویی", "کیسه", 1, 720000, 850000, 890000, 830000, 900000, 4, 27),
    ("6260200000002", "GR-2002", "روغن سرخ‌کردنی ۱.۸ لیتری", "عدد", 6, 148000, 175000, 182000, 170000, 188000, 6, 40),
    ("6260300000001", "DR-3001", "نوشابه خانواده ۱.۵ لیتری", "عدد", 6, 28000, 35000, 37000, 34000, 38000, 24, 120),
    ("6260300000002", "DR-3002", "آب معدنی ۵۰۰ میلی‌لیتری", "بسته", 12, 42000, 52000, 55000, 50000, 57000, 20, 8),
    ("6260300000003", "DR-3003", "چای کیسه‌ای ۱۰۰ عددی", "عدد", 12, 96000, 115000, 120000, 110000, 125000, 6, 52),
]

CUSTOMERS = [
    ("فروشگاه زنجیره‌ای آفتاب", "09121234567"),
    ("سوپرمارکت نگین", "09127654321"),
    ("رستوران باغ ایرانی", "09121112233"),
    ("حسین محمدی", "09351114455"),
    ("مینا رضایی", "09192223344"),
]


def _product(db, code):
    return db.fetch_one("SELECT * FROM products WHERE code = ?;", (code,))


def _customer(db, phone):
    return db.fetch_one("SELECT * FROM parties WHERE phone = ?;", (phone,))


def _sale_item(product, qty_num=1, qty_box=0, **overrides):
    item = {
        "product_id": product["id"],
        "qty_num": qty_num,
        "qty_box": qty_box,
        "units_per_box": product["units_per_box"],
        "price": product["sell_price_1"],
        "price_tier": 1,
    }
    item.update(overrides)
    return item


def seed_demo_data(db):
    inventory = InventoryModule()
    sales = SalesModule()
    customers = CustomerModule()

    for barcode, code, name, unit, upb, buy, s1, s2, s3, s4, min_stock, stock in PRODUCTS:
        product_id = inventory.add_product(
            barcode, code, name, unit, upb, buy, s1, s2, s3, s4, min_stock
        )
        db.execute("UPDATE products SET stock_qty = ? WHERE id = ?;", (stock, product_id))

    customer_ids = {phone: customers.create_customer(name, phone) for name, phone in CUSTOMERS}
    supplier_id = db.execute(
        "INSERT INTO parties (name, type, phone, balance) VALUES ('پخش مواد غذایی البرز', 'supplier', '02144556677', 0);"
    )

    admin = db.fetch_one("SELECT * FROM users WHERE username = 'admin';")
    AuthManager.create_user("sara", "sara1234", "سارا احمدی", "cashier", admin["box_id"])
    db.execute("INSERT INTO cash_boxes (name, is_active) VALUES ('صندوق شعبه دوم', 1);")

    milk = _product(db, "LB-1001")
    yogurt = _product(db, "LB-1002")
    cheese = _product(db, "LB-1003")
    rice = _product(db, "GR-2001")
    oil = _product(db, "GR-2002")
    soda = _product(db, "DR-3001")
    tea = _product(db, "DR-3003")

    first_sale, _, _ = sales.create_sale_invoice(
        customer_ids["09121234567"], admin["id"], admin["box_id"], "cash",
        [
            _sale_item(milk, qty_num=6, qty_box=1),
            _sale_item(yogurt, qty_num=2),
            _sale_item(cheese, qty_num=4),
        ],
    )
    sales.create_sale_invoice(
        customer_ids["09127654321"], admin["id"], admin["box_id"], "credit",
        [
            _sale_item(rice, qty_num=1),
            _sale_item(oil, qty_num=2),
            _sale_item(tea, qty_num=1, has_tax=True, tax_percent=9),
        ],
        invoice_discount=50000,
    )
    sales.create_sale_invoice(
        customer_ids["09121112233"], admin["id"], admin["box_id"], "credit",
        [_sale_item(rice, qty_num=2), _sale_item(yogurt, qty_num=3)],
    )
    sales.create_sale_invoice(
        None, admin["id"], admin["box_id"], "cash",
        [_sale_item(soda, qty_num=4)],
    )

    PurchaseModule().create_purchase_invoice(
        supplier_id, admin["id"], admin["box_id"], "credit",
        [
            dict(_sale_item(milk, qty_num=0, qty_box=3), price=32000),
            dict(_sale_item(yogurt, qty_num=0, qty_box=2), price=85000, gift_qty=1),
        ],
    )

    checks = CheckModule()
    checks.register_check(
        "458912", "بانک ملت", 12500000, "20261215", "received",
        customer_ids["09127654321"], admin["box_id"], admin["id"], "چک فروش نسیه",
    )
    collected_id = checks.register_check(
        "771204", "بانک صادرات", 4800000, "20261120", "received",
        customer_ids["09121112233"], admin["box_id"], admin["id"], "چک رستوران",
    )
    checks.mark_collected(collected_id, admin["id"])
    checks.register_check(
        "990331", "بانک ملی", 7000000, "20261201", "issued",
        supplier_id, admin["box_id"], admin["id"], "چک تامین‌کننده",
    )

    ModianModule().save_as_ready(first_sale, tax_id="14012345678")


def _populate_sales_page(page, db):
    cart = page.tabs.currentWidget()
    milk = _product(db, "LB-1001")
    yogurt = _product(db, "LB-1002")
    cheese = _product(db, "LB-1003")

    def cart_item(product, qty_num, qty_box=0):
        return {
            "product_id": product["id"],
            "name": product["name"],
            "qty_num": qty_num,
            "qty_box": qty_box,
            "prices": {
                1: product["sell_price_1"],
                2: product["sell_price_2"],
                3: product["sell_price_3"],
                4: product["sell_price_4"],
            },
            "price_tier": 1,
            "price": product["sell_price_1"],
            "units_per_box": product["units_per_box"],
        }

    cart.cart_items = [
        cart_item(milk, 6, 1),
        cart_item(yogurt, 2),
        cart_item(cheese, 4),
    ]
    cart.txt_customer_phone.setText("09121234567")
    cart.txt_customer_name.setText("فروشگاه زنجیره‌ای آفتاب")
    cart._render_cart()


def _populate_purchase_page(page, db):
    milk = _product(db, "LB-1001")
    tea = _product(db, "DR-3003")

    def purchase_item(product, qty_num=0, qty_box=1, gift_qty=0):
        return {
            "product_id": product["id"],
            "barcode": product["barcode"],
            "code": product["code"],
            "name": product["name"],
            "qty_num": qty_num,
            "qty_box": qty_box,
            "gift_qty": gift_qty,
            "units_per_box": product["units_per_box"],
            "price": product["buy_price"],
            "discount_amount": 0,
            "discount_type": "rial",
            "has_tax": True,
            "tax_percent": 9,
        }

    page.items_data = [
        purchase_item(milk, qty_box=3),
        purchase_item(tea, qty_num=24, qty_box=0, gift_qty=2),
    ]
    page._render_table()


def _populate_customers_page(page):
    table = page.tab_list.table
    target = next(
        (
            row
            for row in range(table.rowCount())
            if table.item(row, 1) and "آفتاب" in table.item(row, 1).text()
        ),
        0 if table.rowCount() else -1,
    )
    if target >= 0:
        table.setCurrentCell(target, 1)


def capture(window, page_key=None, filename=None, populate=None):
    if page_key:
        window.switch_page(page_key)
    QApplication.processEvents()
    if populate is not None:
        populate(window.pages[page_key])
        QApplication.processEvents()
        populate(window.pages[page_key])
    pixmap = window.grab()
    path = OUTPUT_DIR / filename
    pixmap.save(str(path), "PNG")
    print(f"saved {path.relative_to(ROOT)} ({pixmap.width()}x{pixmap.height()})")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    demo_db = Path(tempfile.gettempdir()) / "dima_screenshots_demo.db"
    if demo_db.exists():
        demo_db.unlink()

    DBManager._instance = None
    AuthManager._instance = None
    db = DBManager(db_path=str(demo_db))
    seed_demo_data(db)

    app = QApplication(sys.argv)
    set_language("fa")

    style_path = ROOT / "ui" / "style.qss"
    if style_path.exists():
        app.setStyleSheet(style_path.read_text(encoding="utf-8"))

    assert AuthManager.instance().login("admin", "admin123") is not None

    window = MainWindow()
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    window.resize(*WINDOW_SIZE)
    window.show()
    QApplication.processEvents()

    _populate_sales_page(window.pages["sales"], db)
    _populate_purchase_page(window.pages["purchase"], db)
    pages = [
        ("dashboard", "dashboard.png"),
        ("sales", "sales.png"),
        ("purchase", "purchase.png"),
        ("invoices", "invoices.png"),
        ("inventory", "inventory.png"),
        ("customers", "customers.png"),
        ("treasury", "treasury.png"),
        ("checks", "checks.png"),
        ("accounting", "accounting.png"),
        ("settings", "settings.png"),
        ("about", "about.png"),
    ]
    for page_key, filename in pages:
        populate = _populate_customers_page if page_key == "customers" else None
        capture(window, page_key, filename, populate=populate)

    window.close()
    AuthManager.instance().logout()

    login = LoginWindow()
    login.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    login.show()
    QApplication.processEvents()
    pixmap = login.grab()
    pixmap.save(str(OUTPUT_DIR / "login.png"), "PNG")
    print(f"saved docs/screenshots/login.png ({pixmap.width()}x{pixmap.height()})")

    db.close()


if __name__ == "__main__":
    main()
