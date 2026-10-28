# -*- coding: utf-8 -*-
"""
modules/inventory.py
----------------------
منطق تجاری مربوط به کالا و انبار.
پشتیبانی از واحدهای مرکب (عدد/جعبه) با ضریب تبدیل units_per_box.
"""

from core.db_manager import DBManager


class InventoryModule:
    def __init__(self):
        self.db = DBManager.instance()

    # ------------------- CRUD کالا -------------------
    def add_product(self, barcode, code, name, unit_type, units_per_box,
                     buy_price, sell_price_1, sell_price_2, sell_price_3, sell_price_4,
                     min_stock, group_main_id=None, group_sub_id=None):
        """
        افزودن کالای جدید با ۴ سطح قیمت فروش (مثلاً نقدی/نسیه/قدیم/جدید طبق
        برچسب‌های قابل‌تنظیم در price_tier_labels) و گروه‌بندی اصلی/فرعی.
        این متد فقط باید از UI مدیریت کالا (قابل‌دسترس برای ادمین/حسابدار) صدا زده شود.
        """
        return self.db.execute(
            """INSERT INTO products
               (barcode, code, name, unit_type, units_per_box, buy_price,
                sell_price_1, sell_price_2, sell_price_3, sell_price_4,
                group_main_id, group_sub_id, min_stock)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            (barcode, code, name, unit_type, units_per_box, buy_price,
             sell_price_1, sell_price_2, sell_price_3, sell_price_4,
             group_main_id, group_sub_id, min_stock),
        )

    # ------------------- سطوح قیمت (برچسب‌های قابل تنظیم) -------------------
    def get_price_tier_labels(self):
        """
        بازگرداندن برچسب هر یک از ۴ سطح قیمت (مثلاً «قیمت نقدی»، «قیمت قدیم» و ...).
        این برچسب‌ها هم در فرم مدیریت کالا و هم در فاکتور فروش (برای صندوق‌دار) استفاده می‌شوند.
        """
        rows = self.db.fetch_all(
            "SELECT tier_number, label FROM price_tier_labels ORDER BY tier_number;"
        )
        return {row["tier_number"]: row["label"] for row in rows}

    def update_price_tier_label(self, tier_number: int, new_label: str):
        """
        تغییر برچسب یک سطح قیمت. فقط باید توسط ادمین/حسابدار از صفحه تنظیمات صدا زده شود؛
        بررسی سطح دسترسی در لایه UI (AuthManager.can_manage_products) انجام می‌شود.
        """
        self.db.execute(
            "UPDATE price_tier_labels SET label = ? WHERE tier_number = ?;",
            (new_label, tier_number),
        )

    # ------------------- گروه‌بندی کالا -------------------
    def get_main_groups(self):
        return self.db.fetch_all(
            "SELECT * FROM product_categories WHERE parent_id IS NULL ORDER BY name;"
        )

    def get_sub_groups(self, main_group_id):
        return self.db.fetch_all(
            "SELECT * FROM product_categories WHERE parent_id = ? ORDER BY name;",
            (main_group_id,),
        )

    def add_category(self, name, parent_id=None):
        return self.db.execute(
            "INSERT INTO product_categories (name, parent_id) VALUES (?, ?);",
            (name, parent_id),
        )

    def update_product(self, product_id, **fields):
        """به‌روزرسانی پویا؛ فقط فیلدهای ارسال شده تغییر می‌کنند."""
        if not fields:
            return
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
        params = tuple(fields.values()) + (product_id,)
        self.db.execute(f"UPDATE products SET {set_clause} WHERE id = ?;", params)

    def delete_product(self, product_id):
        self.db.execute("DELETE FROM products WHERE id = ?;", (product_id,))

    def find_by_barcode(self, barcode):
        return self.db.fetch_one("SELECT * FROM products WHERE barcode = ?;", (barcode,))

    def search_products(self, keyword: str):
        like = f"%{keyword}%"
        return self.db.fetch_all(
            """SELECT * FROM products
               WHERE name LIKE ? OR code LIKE ? OR barcode LIKE ?
               ORDER BY name;""",
            (like, like, like),
        )

    def get_all_products(self):
        return self.db.fetch_all("SELECT * FROM products ORDER BY name;")

    # ------------------- تبدیل واحد مرکب (عدد/جعبه) -------------------
    @staticmethod
    def convert_to_base_units(qty_num: float, qty_box: float, units_per_box: int) -> float:
        """
        محاسبه‌ی تعداد کل بر حسب واحد پایه (عدد) با توجه به ضریب تبدیل جعبه.
        مثال: اگر units_per_box=12 و qty_box=2 و qty_num=3 => 27 عدد
        """
        return qty_num + (qty_box * units_per_box)

    # ------------------- به‌روزرسانی موجودی -------------------
    def adjust_stock(self, cursor, product_id: int, delta_qty: float):
        """
        افزایش/کاهش موجودی کالا در بستر یک تراکنش موجود (cursor).
        delta_qty مثبت برای افزایش (خرید) و منفی برای کاهش (فروش) است.
        این متد باید همیشه داخل db.transaction() فراخوانی شود تا با ثبت فاکتور اتمیک بماند.
        """
        cursor.execute(
            "UPDATE products SET stock_qty = stock_qty + ? WHERE id = ?;",
            (delta_qty, product_id),
        )

    def get_low_stock_products(self):
        """هشدار نقطه سفارش: کالاهایی که موجودی آن‌ها به حداقل مجاز رسیده یا کمتر است."""
        return self.db.fetch_all(
            "SELECT * FROM products WHERE stock_qty <= min_stock ORDER BY stock_qty ASC;"
        )
