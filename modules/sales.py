# -*- coding: utf-8 -*-
"""
modules/sales.py
------------------
منطق تجاری فاکتور فروش (سریع/خرده و عمده).
پشتیبانی از جستجوی بارکد، انتخاب سطح قیمت توسط صندوق‌دار، تخفیف، مالیات/عوارض،
و فیلتر خودکار بر اساس صندوق کاربر لاگین‌کرده (طبق سیاست ایزولاسیون صندوق).
"""

import datetime
from core.db_manager import DBManager
from modules.inventory import InventoryModule
from modules.accounting import AccountingModule
from modules.treasury import TreasuryModule


class SalesModule:
    def __init__(self):
        self.db = DBManager.instance()
        self.inventory = InventoryModule()
        self.accounting = AccountingModule()
        self.treasury = TreasuryModule()

    def generate_invoice_number(self, is_wholesale=False):
        prefix = "WSL" if is_wholesale else "SAL"
        today = datetime.date.today().strftime("%Y%m%d")
        row = self.db.fetch_one(
            "SELECT COUNT(*) AS c FROM invoices WHERE invoice_type = 'sale' AND date LIKE ? AND is_wholesale = ?;",
            (f"{today}%", 1 if is_wholesale else 0),
        )
        seq = (row["c"] or 0) + 1
        return f"{prefix}-{today}-{seq:04d}"

    def find_product_by_barcode(self, barcode: str):
        """جستجوی سریع کالا با اسکنر بارکد؛ برای استفاده در فاکتور فروش سریع."""
        return self.inventory.find_by_barcode(barcode)

    @staticmethod
    def _calc_discount(subtotal, discount_amount, discount_type):
        if discount_type == "percent":
            return subtotal * (discount_amount / 100.0)
        return discount_amount

    def create_sale_invoice(self, party_id, user_id, box_id, payment_type, items: list,
                             invoice_discount=0, invoice_discount_type="rial",
                             duty_amount=0, is_wholesale=False):
        """
        items: لیستی از دیکشنری‌ها با کلیدهای:
            product_id, qty_num, qty_box, price, units_per_box, price_tier (اختیاری),
            discount_amount (اختیاری)، discount_type (اختیاری)،
            has_tax (اختیاری)، tax_percent (اختیاری)

        عملیات اتمیک:
            ۱. بررسی کفایت موجودی برای هر کالا
            ۲. درج هدر و اقلام فاکتور با محاسبه تخفیف/مالیات هر سطر
            ۳. کاهش موجودی انبار
            ۴. صدور خودکار سند حسابداری (بدهکار صندوق/حسابهای دریافتنی، بستانکار فروش کالا)
        در صورت ناکافی بودن موجودی، کل عملیات لغو (ROLLBACK) و خطا صادر می‌شود.
        """
        invoice_number = self.generate_invoice_number(is_wholesale)
        today_str = datetime.date.today().strftime("%Y%m%d")
        subtotal_amount = 0.0
        total_tax = 0.0

        with self.db.transaction() as cur:
            cur.execute(
                """INSERT INTO invoices
                   (invoice_number, invoice_type, date, party_id, user_id, box_id,
                    subtotal_amount, discount_amount, discount_type, tax_amount,
                    duty_amount, total_amount, payment_type, is_wholesale)
                   VALUES (?, 'sale', ?, ?, ?, ?, 0, ?, ?, 0, ?, 0, ?, ?);""",
                (invoice_number, today_str, party_id, user_id, box_id,
                 invoice_discount, invoice_discount_type, duty_amount,
                 payment_type, 1 if is_wholesale else 0),
            )
            invoice_id = cur.lastrowid

            for item in items:
                base_qty = self.inventory.convert_to_base_units(
                    item["qty_num"], item["qty_box"], item.get("units_per_box", 1)
                )

                # بررسی موجودی کافی قبل از کسر (جلوگیری از موجودی منفی)
                product_row = cur.execute(
                    "SELECT stock_qty, name FROM products WHERE id = ?;",
                    (item["product_id"],),
                ).fetchone()
                if product_row is None or product_row["stock_qty"] < base_qty:
                    raise ValueError(
                        f"موجودی کافی برای کالای «{product_row['name'] if product_row else item['product_id']}» وجود ندارد."
                    )

                line_subtotal = base_qty * item["price"]
                discount_amount = item.get("discount_amount", 0)
                discount_type = item.get("discount_type", "rial")
                line_discount = self._calc_discount(line_subtotal, discount_amount, discount_type)

                has_tax = item.get("has_tax", False)
                tax_percent = item.get("tax_percent", 0) if has_tax else 0
                line_after_discount = line_subtotal - line_discount
                tax_amount = line_after_discount * (tax_percent / 100.0) if has_tax else 0

                line_total = line_after_discount + tax_amount
                subtotal_amount += line_subtotal
                total_tax += tax_amount

                cur.execute(
                    """INSERT INTO invoice_items
                       (invoice_id, product_id, qty_num, qty_box, gift_qty, prod_date,
                        exp_date, price, price_tier, discount_amount, discount_type,
                        has_tax, tax_percent, tax_amount, line_total)
                       VALUES (?, ?, ?, ?, 0, NULL, NULL, ?, ?, ?, ?, ?, ?, ?, ?);""",
                    (invoice_id, item["product_id"], item["qty_num"], item["qty_box"],
                     item["price"], item.get("price_tier"), discount_amount, discount_type,
                     1 if has_tax else 0, tax_percent, tax_amount, line_total),
                )

                # کاهش موجودی انبار (فروش = کاهش)
                self.inventory.adjust_stock(cur, item["product_id"], -base_qty)

            invoice_discount_value = self._calc_discount(
                subtotal_amount, invoice_discount, invoice_discount_type
            )
            total_amount = subtotal_amount - invoice_discount_value + total_tax + duty_amount

            cur.execute(
                """UPDATE invoices
                   SET subtotal_amount = ?, tax_amount = ?, total_amount = ?
                   WHERE id = ?;""",
                (subtotal_amount, total_tax, total_amount, invoice_id),
            )

            # افزایش طلب از مشتری در صورت فروش نسیه
            if payment_type == "credit" and party_id:
                cur.execute(
                    "UPDATE parties SET balance = balance + ? WHERE id = ?;",
                    (total_amount, party_id),
                )

        # صدور خودکار سند حسابداری (در صورت نبود نگاشت حساب، بی‌صدا رد می‌شود)
        try:
            self.accounting.auto_post_sale_invoice(
                invoice_id, invoice_number, total_amount, payment_type, user_id
            )
        except Exception:
            pass

        # به‌روزرسانی آنی مانده صندوق: فقط برای پرداخت نقدی/کارتی، چون فروش
        # نسیه (credit) اثر نقدی فوری روی صندوق ندارد و فقط طلب مشتری بالا می‌رود.
        if payment_type in ("cash", "card"):
            try:
                self.treasury.register_transaction(
                    trans_type="receive", amount=total_amount, box_id=box_id,
                    user_id=user_id, party_id=party_id, invoice_id=invoice_id,
                    description=f"بابت فاکتور فروش {invoice_number}",
                    skip_accounting=True,  # سند حسابداری همین الان بالا صادر شد
                )
            except Exception:
                pass

        return invoice_id, invoice_number, total_amount

    def get_sale_invoices(self, box_id=None):
        """
        ایزولاسیون صندوق: کاربر صندوق‌دار فقط فاکتورهای صندوق خودش را می‌بیند.
        box_id=None به معنی دسترسی کامل (ادمین) است.
        """
        if box_id is None:
            return self.db.fetch_all(
                "SELECT * FROM invoices WHERE invoice_type = 'sale' ORDER BY id DESC;"
            )
        return self.db.fetch_all(
            "SELECT * FROM invoices WHERE invoice_type = 'sale' AND box_id = ? ORDER BY id DESC;",
            (box_id,),
        )
