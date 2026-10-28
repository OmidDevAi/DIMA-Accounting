# -*- coding: utf-8 -*-
"""
modules/purchase.py
---------------------
منطق تجاری فاکتور خرید.
ثبت فاکتور خرید شامل: هدر فاکتور + اقلام (با مقدار هدیه، تخفیف، مالیات/عوارض)
+ افزایش موجودی انبار + صدور خودکار سند حسابداری،
همه در یک تراکنش اتمیک (BEGIN/COMMIT/ROLLBACK) انجام می‌شود.
"""

import datetime
from core.db_manager import DBManager
from modules.inventory import InventoryModule
from modules.accounting import AccountingModule
from modules.treasury import TreasuryModule


class PurchaseModule:
    def __init__(self):
        self.db = DBManager.instance()
        self.inventory = InventoryModule()
        self.accounting = AccountingModule()
        self.treasury = TreasuryModule()

    def generate_invoice_number(self):
        """تولید شماره فاکتور خودکار بر اساس تاریخ و شمارنده."""
        today = datetime.date.today().strftime("%Y%m%d")
        row = self.db.fetch_one(
            "SELECT COUNT(*) AS c FROM invoices WHERE invoice_type = 'purchase' AND date LIKE ?;",
            (f"{today}%",),
        )
        seq = (row["c"] or 0) + 1
        return f"PUR-{today}-{seq:04d}"

    @staticmethod
    def _calc_discount(subtotal, discount_amount, discount_type):
        if discount_type == "percent":
            return subtotal * (discount_amount / 100.0)
        return discount_amount

    def create_purchase_invoice(self, party_id, user_id, box_id, payment_type, items: list,
                                 invoice_discount=0, invoice_discount_type="rial",
                                 duty_amount=0, is_wholesale=False):
        """
        items: لیستی از دیکشنری‌ها با کلیدهای:
            product_id, qty_num, qty_box, gift_qty (اختیاری، پیش‌فرض ۰),
            prod_date, exp_date, price, units_per_box,
            discount_amount (اختیاری)، discount_type ('rial'/'percent'، اختیاری)،
            has_tax (اختیاری، بولی)، tax_percent (اختیاری، مثلاً ۹ برای ۹٪ ارزش افزوده)

        مقدار هدیه (gift_qty) به موجودی انبار اضافه می‌شود ولی در محاسبه‌ی
        جمع مبلغ فاکتور لحاظ نمی‌شود (کالای رایگان از طرف تامین‌کننده).

        عملیات به صورت اتمیک انجام می‌شود:
            ۱. درج هدر فاکتور
            ۲. درج تک‌تک اقلام با محاسبه تخفیف/مالیات هر سطر
            ۳. افزایش موجودی هر کالا به میزان (مقدار خریداری‌شده + مقدار هدیه)
            ۴. صدور خودکار سند حسابداری (بدهکار موجودی کالا / بستانکار صندوق یا حسابهای پرداختنی)
        """
        invoice_number = self.generate_invoice_number()
        today_str = datetime.date.today().strftime("%Y%m%d")
        subtotal_amount = 0.0
        total_tax = 0.0

        with self.db.transaction() as cur:
            # ۱. درج هدر فاکتور (ابتدا با مبالغ صفر، سپس در پایان به‌روزرسانی می‌شود)
            cur.execute(
                """INSERT INTO invoices
                   (invoice_number, invoice_type, date, party_id, user_id, box_id,
                    subtotal_amount, discount_amount, discount_type, tax_amount,
                    duty_amount, total_amount, payment_type, is_wholesale)
                   VALUES (?, 'purchase', ?, ?, ?, ?, 0, ?, ?, 0, ?, 0, ?, ?);""",
                (invoice_number, today_str, party_id, user_id, box_id,
                 invoice_discount, invoice_discount_type, duty_amount,
                 payment_type, 1 if is_wholesale else 0),
            )
            invoice_id = cur.lastrowid

            # ۲. درج اقلام فاکتور + افزایش موجودی
            for item in items:
                gift_qty = item.get("gift_qty", 0)
                base_qty = self.inventory.convert_to_base_units(
                    item["qty_num"], item["qty_box"], item.get("units_per_box", 1)
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
                        exp_date, price, discount_amount, discount_type,
                        has_tax, tax_percent, tax_amount, line_total)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                    (invoice_id, item["product_id"], item["qty_num"], item["qty_box"], gift_qty,
                     item.get("prod_date"), item.get("exp_date"), item["price"],
                     discount_amount, discount_type, 1 if has_tax else 0, tax_percent,
                     tax_amount, line_total),
                )

                # افزایش موجودی انبار: مقدار خریداری‌شده + مقدار هدیه (رایگان)
                self.inventory.adjust_stock(cur, item["product_id"], base_qty + gift_qty)

                # به‌روزرسانی آخرین قیمت خرید کالا
                cur.execute(
                    "UPDATE products SET buy_price = ? WHERE id = ?;",
                    (item["price"], item["product_id"]),
                )

            # محاسبه تخفیف کل فاکتور (روی جمع جزء)
            invoice_discount_value = self._calc_discount(
                subtotal_amount, invoice_discount, invoice_discount_type
            )
            total_amount = subtotal_amount - invoice_discount_value + total_tax + duty_amount

            # ۳. به‌روزرسانی جمع کل فاکتور
            cur.execute(
                """UPDATE invoices
                   SET subtotal_amount = ?, tax_amount = ?, total_amount = ?
                   WHERE id = ?;""",
                (subtotal_amount, total_tax, total_amount, invoice_id),
            )

            # افزایش بدهی به تامین‌کننده در صورت نسیه بودن
            if payment_type == "credit" and party_id:
                cur.execute(
                    "UPDATE parties SET balance = balance - ? WHERE id = ?;",
                    (total_amount, party_id),
                )

        # ۴. صدور خودکار سند حسابداری (خارج از تراکنش اصلی چون خودش تراکنش مستقل دارد؛
        #    در صورت عدم تنظیم نگاشت حساب‌ها، بی‌صدا نادیده گرفته می‌شود تا مانع فاکتور نشود)
        try:
            self.accounting.auto_post_purchase_invoice(
                invoice_id, invoice_number, total_amount, payment_type, user_id
            )
        except Exception:
            pass

        # به‌روزرسانی آنی مانده صندوق: فقط برای پرداخت نقدی/کارتی
        if payment_type in ("cash", "card"):
            try:
                self.treasury.register_transaction(
                    trans_type="pay", amount=total_amount, box_id=box_id,
                    user_id=user_id, party_id=party_id, invoice_id=invoice_id,
                    description=f"بابت فاکتور خرید {invoice_number}",
                    skip_accounting=True,
                )
            except Exception:
                pass

        return invoice_id, invoice_number, total_amount

    def get_purchase_invoices(self, box_id=None):
        """
        دریافت لیست فاکتورهای خرید.
        اگر box_id مشخص شود (کاربر صندوق‌دار)، فقط فاکتورهای همان صندوق برگردانده می‌شود.
        برای ادمین (box_id=None) همه فاکتورها نمایش داده می‌شود.
        """
        if box_id is None:
            return self.db.fetch_all(
                "SELECT * FROM invoices WHERE invoice_type = 'purchase' ORDER BY id DESC;"
            )
        return self.db.fetch_all(
            "SELECT * FROM invoices WHERE invoice_type = 'purchase' AND box_id = ? ORDER BY id DESC;",
            (box_id,),
        )
