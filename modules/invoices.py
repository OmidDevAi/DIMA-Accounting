# -*- coding: utf-8 -*-
"""
modules/invoices.py
----------------------
مشاهده‌ی تاریخچه‌ی همه‌ی فاکتورها (فروش و خرید) و حذف کامل یک فاکتور.

حذف فاکتور یک عملیات «برگشت کامل» است، نه فقط پاک کردن یک ردیف؛ چون یک
فاکتور می‌تواند اثرات جانبی زیادی گذاشته باشد (تغییر موجودی انبار، تغییر
مانده حساب مشتری/تامین‌کننده، تراکنش خزانه، سند حسابداری خودکار). این ماژول
همه‌ی این اثرات را قبل از حذف فاکتور برمی‌گرداند تا دفاتر و موجودی دقیق بمانند.
"""

from core.db_manager import DBManager


class InvoiceModule:
    def __init__(self):
        self.db = DBManager.instance()

    def get_all_invoices(self, box_id=None, invoice_type=None):
        """
        فهرست فاکتورها (فروش و/یا خرید).
        box_id=None یعنی دسترسی کامل (ادمین)؛ در غیر این صورت طبق قانون
        ایزولاسیون صندوق، فقط فاکتورهای همان صندوق برگردانده می‌شود.
        """
        query = """
            SELECT i.*, p.name AS party_name, u.full_name AS user_name
            FROM invoices i
            LEFT JOIN parties p ON i.party_id = p.id
            LEFT JOIN users u ON i.user_id = u.id
            WHERE 1=1
        """
        params = []
        if box_id is not None:
            query += " AND i.box_id = ?"
            params.append(box_id)
        if invoice_type:
            query += " AND i.invoice_type = ?"
            params.append(invoice_type)
        query += " ORDER BY i.id DESC;"
        return self.db.fetch_all(query, tuple(params))

    def get_invoice_items(self, invoice_id):
        return self.db.fetch_all(
            """SELECT ii.*, p.name AS product_name, p.code AS product_code
               FROM invoice_items ii JOIN products p ON ii.product_id = p.id
               WHERE ii.invoice_id = ?;""",
            (invoice_id,),
        )

    def delete_invoice(self, invoice_id):
        """
        حذف کامل یک فاکتور و برگرداندن همه‌ی اثرات جانبی آن:
            ۱. موجودی انبار هر کالا برمی‌گردد (فروش: موجودی افزایش می‌یابد؛
               خرید: موجودی از جمله مقدار هدیه کاهش می‌یابد)
            ۲. مانده‌ی حساب مشتری/تامین‌کننده (در صورت نسیه بودن) برگردانده می‌شود
            ۳. تراکنش خزانه‌ی مرتبط (در صورت نقدی/کارتی بودن) حذف می‌شود
            ۴. سند حسابداری خودکار مرتبط حذف می‌شود
            ۵. خودِ فاکتور حذف می‌شود (اقلامش با CASCADE خودکار حذف می‌شوند)؛
               سابقه‌ی آماده‌سازی مودیان حفظ می‌شود و فقط از فاکتور جدا می‌گردد
        همه‌ی این مراحل در یک تراکنش اتمیک انجام می‌شوند.
        """
        invoice = self.db.fetch_one("SELECT * FROM invoices WHERE id = ?;", (invoice_id,))
        if invoice is None:
            raise ValueError("فاکتور یافت نشد.")

        items = self.db.fetch_all(
            "SELECT * FROM invoice_items WHERE invoice_id = ?;", (invoice_id,)
        )

        with self.db.transaction() as cur:
            # ۱. برگرداندن موجودی انبار
            for item in items:
                product = cur.execute(
                    "SELECT units_per_box FROM products WHERE id = ?;", (item["product_id"],)
                ).fetchone()
                units_per_box = product["units_per_box"] if product else 1
                base_qty = item["qty_num"] + (item["qty_box"] * units_per_box)

                if invoice["invoice_type"] == "sale":
                    cur.execute(
                        "UPDATE products SET stock_qty = stock_qty + ? WHERE id = ?;",
                        (base_qty, item["product_id"]),
                    )
                else:  # purchase
                    total_added = base_qty + item["gift_qty"]
                    cur.execute(
                        "UPDATE products SET stock_qty = stock_qty - ? WHERE id = ?;",
                        (total_added, item["product_id"]),
                    )

            # ۲. برگرداندن مانده‌ی حساب طرف (فقط در صورت نسیه بودن)
            if invoice["payment_type"] == "credit" and invoice["party_id"]:
                if invoice["invoice_type"] == "sale":
                    cur.execute(
                        "UPDATE parties SET balance = balance - ? WHERE id = ?;",
                        (invoice["total_amount"], invoice["party_id"]),
                    )
                else:
                    cur.execute(
                        "UPDATE parties SET balance = balance + ? WHERE id = ?;",
                        (invoice["total_amount"], invoice["party_id"]),
                    )

            # ۳. حذف تراکنش خزانه‌ی مرتبط (در صورت نقدی/کارتی بودن)
            cur.execute("DELETE FROM treasury_transactions WHERE invoice_id = ?;", (invoice_id,))

            # ۴. حذف سند حسابداری خودکار مرتبط (ردیف‌های سند با CASCADE حذف می‌شوند)
            cur.execute(
                "DELETE FROM journal_entries WHERE source_type = ? AND source_id = ?;",
                (invoice["invoice_type"], invoice_id),
            )

            # ۵. حذف خود فاکتور (اقلام با ON DELETE CASCADE خودکار حذف می‌شوند)
            cur.execute("DELETE FROM invoices WHERE id = ?;", (invoice_id,))

        return True
