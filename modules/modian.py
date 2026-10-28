# -*- coding: utf-8 -*-
"""
modules/modian.py
--------------------
آماده‌سازی ساختار داده برای ارسال صورتحساب الکترونیکی به «سامانه مودیان»
(سازمان امور مالیاتی ایران - fa.tax.gov.ir).

⚠️ نکته مهم:
    این ماژول فقط «ساختار داده» و فرآیند آماده‌سازی را پیاده می‌کند.
    اتصال واقعی به API سامانه مودیان نیازمند موارد زیر است که در این
    نسخه پیاده‌سازی نشده و باید توسط توسعه‌دهنده تکمیل شود:
        - گواهی دیجیتال ثبت‌شده در سامانه مودیان (برای امضای دیجیتال صورتحساب)
        - شناسه یکتای حافظه مالیاتی (Tax Identification Number شرکت)
        - آدرس سرویس API واقعی سازمان امور مالیاتی و توکن دسترسی
    به همین دلیل، وضعیت هر سند حداکثر تا 'ready' (آماده ارسال) پیش می‌رود
    و متد send_to_modian() در این نسخه به‌صورت عمدی NotImplementedError می‌دهد.
"""

import json
import datetime
from core.db_manager import DBManager


class ModianModule:
    def __init__(self):
        self.db = DBManager.instance()

    # =================================================================
    # تنظیمات اتصال (لینک API و گواهی دیجیتال)
    # =================================================================
    def get_settings(self):
        """
        بازگرداندن تنظیمات فعلی اتصال به سامانه مودیان.
        اگر هنوز چیزی ذخیره نشده باشد، مقادیر خالی برمی‌گرداند.
        """
        row = self.db.fetch_one("SELECT * FROM modian_settings WHERE id = 1;")
        if row is None:
            return {"api_url": "", "certificate_path": ""}
        return {"api_url": row["api_url"] or "", "certificate_path": row["certificate_path"] or ""}

    def save_settings(self, api_url, certificate_path):
        """
        ذخیره‌ی لینک API و مسیر فایل گواهی دیجیتال.
        ⚠️ ذخیره‌ی این مقادیر به‌تنهایی اتصال واقعی به سامانه مودیان را فعال
        نمی‌کند؛ send_to_modian() هنوز باید توسط توسعه‌دهنده تکمیل شود تا
        واقعاً از این تنظیمات برای امضا و ارسال HTTP استفاده کند.
        """
        existing = self.db.fetch_one("SELECT id FROM modian_settings WHERE id = 1;")
        if existing:
            self.db.execute(
                "UPDATE modian_settings SET api_url = ?, certificate_path = ? WHERE id = 1;",
                (api_url, certificate_path),
            )
        else:
            self.db.execute(
                "INSERT INTO modian_settings (id, api_url, certificate_path) VALUES (1, ?, ?);",
                (api_url, certificate_path),
            )

    def prepare_invoice_payload(self, invoice_id):
        """
        ساخت ساختار داده‌ی صورتحساب الکترونیکی بر اساس فاکتور فروش موجود،
        با فیلدهای پرکاربرد سامانه مودیان (نگاشت تقریبی؛ نام دقیق فیلدها
        باید طبق آخرین مستندات سازمان امور مالیاتی نهایی شود):
            - shamsi_date: تاریخ شمسی سند
            - total_amount: مبلغ کل فاکتور
            - tax_amount: مالیات بر ارزش افزوده
            - buyer: اطلاعات خریدار (در صورت وجود شخص)
            - items: اقلام فاکتور با شرح، تعداد، قیمت واحد و مالیات هر ردیف
        """
        invoice = self.db.fetch_one("SELECT * FROM invoices WHERE id = ?;", (invoice_id,))
        if invoice is None:
            raise ValueError("فاکتور یافت نشد.")

        items = self.db.fetch_all(
            """SELECT ii.*, p.name AS product_name, p.code AS product_code
               FROM invoice_items ii JOIN products p ON ii.product_id = p.id
               WHERE ii.invoice_id = ?;""",
            (invoice_id,),
        )

        party = None
        if invoice["party_id"]:
            party = self.db.fetch_one("SELECT * FROM parties WHERE id = ?;", (invoice["party_id"],))

        payload = {
            "invoice_number": invoice["invoice_number"],
            "date": invoice["date"],
            "total_amount": invoice["total_amount"],
            "tax_amount": invoice["tax_amount"],
            "duty_amount": invoice["duty_amount"],
            "discount_amount": invoice["discount_amount"],
            "buyer": {
                "name": party["name"] if party else "مصرف‌کننده نهایی",
                "phone": party["phone"] if party else None,
            },
            "items": [
                {
                    "product_code": item["product_code"],
                    "product_name": item["product_name"],
                    "quantity": item["qty_num"] + item["qty_box"],
                    "unit_price": item["price"],
                    "tax_percent": item["tax_percent"],
                    "tax_amount": item["tax_amount"],
                    "line_total": item["line_total"],
                }
                for item in items
            ],
        }
        return payload

    def save_as_ready(self, invoice_id, tax_id=None, uid=None):
        """
        ذخیره‌ی سند آماده‌شده با وضعیت 'ready' (آماده ارسال).
        این عملیات سند را واقعاً به سامانه مودیان ارسال نمی‌کند؛ فقط آن را
        در دیتابیس محلی برای ارسال دستی یا اتصال آینده به API آماده می‌سازد.
        """
        payload = self.prepare_invoice_payload(invoice_id)
        payload_json = json.dumps(payload, ensure_ascii=False)
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        existing = self.db.fetch_one(
            "SELECT id FROM modian_invoices WHERE invoice_id = ?;", (invoice_id,)
        )
        if existing:
            self.db.execute(
                """UPDATE modian_invoices
                   SET tax_id = ?, uid = ?, status = 'ready', payload_json = ?, prepared_at = ?
                   WHERE invoice_id = ?;""",
                (tax_id, uid, payload_json, now_str, invoice_id),
            )
        else:
            self.db.execute(
                """INSERT INTO modian_invoices
                   (invoice_id, tax_id, uid, status, payload_json, prepared_at)
                   VALUES (?, ?, ?, 'ready', ?, ?);""",
                (invoice_id, tax_id, uid, payload_json, now_str),
            )
        return payload

    def get_pending_invoices(self):
        """فاکتورهای فروشی که هنوز برای سامانه مودیان آماده یا ارسال نشده‌اند."""
        return self.db.fetch_all(
            """SELECT i.* FROM invoices i
               LEFT JOIN modian_invoices mi ON mi.invoice_id = i.id
               WHERE i.invoice_type = 'sale'
                 AND (mi.id IS NULL OR mi.status IN ('not_prepared', 'failed'))
               ORDER BY i.id DESC;"""
        )

    def get_all_modian_records(self):
        return self.db.fetch_all(
            """SELECT mi.*, i.invoice_number, i.total_amount
               FROM modian_invoices mi JOIN invoices i ON mi.invoice_id = i.id
               ORDER BY mi.id DESC;"""
        )

    def send_to_modian(self, invoice_id):
        """
        ارسال واقعی به سامانه مودیان.
        ⚠️ در این نسخه پیاده‌سازی نشده است چون نیازمند گواهی دیجیتال و دسترسی
        API واقعی سازمان امور مالیاتی است. برای فعال‌سازی این متد باید:
            ۱. کتابخانه امضای دیجیتال و گواهی مربوطه را نصب/پیکربندی کنید.
            ۲. آدرس سرویس و توکن API را در تنظیمات وارد کنید.
            ۳. این متد را با فراخوانی واقعی HTTP به آن سرویس تکمیل کنید.
        """
        raise NotImplementedError(
            "اتصال واقعی به سامانه مودیان در این نسخه پیاده‌سازی نشده است. "
            "این متد فقط محل آماده برای تکمیل آینده توسط توسعه‌دهنده است."
        )
