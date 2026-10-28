# -*- coding: utf-8 -*-
"""
modules/customers.py
----------------------
مدیریت لیست مشتریان (اشخاص از نوع customer در جدول parties):
جستجو، ثبت خودکار مشتری جدید هنگام فروش (فقط با نام و شماره موبایل)،
و مشاهده‌ی تاریخچه‌ی فاکتورهای فروش یک‌سال‌اخیر هر مشتری.
"""

import datetime
from core.db_manager import DBManager


class CustomerModule:
    def __init__(self):
        self.db = DBManager.instance()

    def search_customers(self, keyword: str):
        like = f"%{keyword}%"
        return self.db.fetch_all(
            """SELECT * FROM parties
               WHERE type = 'customer' AND (name LIKE ? OR phone LIKE ?)
               ORDER BY name;""",
            (like, like),
        )

    def get_all_customers(self):
        return self.db.fetch_all("SELECT * FROM parties WHERE type = 'customer' ORDER BY name;")

    def find_by_phone(self, phone: str):
        return self.db.fetch_one(
            "SELECT * FROM parties WHERE type = 'customer' AND phone = ?;", (phone,)
        )

    def create_customer(self, name: str, phone: str):
        """ثبت مشتری جدید فقط با نام و شماره موبایل (بدون هیچ فیلد اجباری دیگر)."""
        return self.db.execute(
            "INSERT INTO parties (name, type, phone, balance) VALUES (?, 'customer', ?, 0);",
            (name, phone),
        )

    def get_or_create_customer(self, phone: str, name: str = None):
        """
        اگر مشتری‌ای با این شماره موبایل قبلاً ثبت شده باشد، همان شناسه برگردانده می‌شود.
        اگر مشتری جدید است و نام هم داده شده، همان لحظه با نام+موبایل ساخته می‌شود.
        اگر مشتری جدید است ولی نامی داده نشده، None برمی‌گردد تا لایه‌ی UI نام را
        از کاربر (صندوق‌دار) بپرسد؛ چون طبق قانون، مشتری جدید حتماً باید نام داشته باشد.
        """
        existing = self.find_by_phone(phone)
        if existing:
            return existing["id"]
        if not name:
            return None
        return self.create_customer(name, phone)

    def get_customer_invoices(self, customer_id, days=365):
        """فاکتورهای فروش یک مشتری در N روز اخیر (پیش‌فرض یک سال)."""
        cutoff = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y%m%d")
        return self.db.fetch_all(
            """SELECT * FROM invoices
               WHERE party_id = ? AND invoice_type = 'sale' AND date >= ?
               ORDER BY date DESC;""",
            (customer_id, cutoff),
        )

    def find_inactive_customers(self, date_from: str, date_to: str):
        """
        مشتریانی که در بازه‌ی [date_from, date_to] (فرمت YYYYMMDD) هیچ
        فاکتور فروشی نداشته‌اند؛ برای کمپین‌های یادآوری/بازگرداندن مشتری استفاده می‌شود.
        """
        return self.db.fetch_all(
            """SELECT * FROM parties
               WHERE type = 'customer'
                 AND id NOT IN (
                     SELECT DISTINCT party_id FROM invoices
                     WHERE invoice_type = 'sale' AND party_id IS NOT NULL
                       AND date BETWEEN ? AND ?
                 )
               ORDER BY name;""",
            (date_from, date_to),
        )
