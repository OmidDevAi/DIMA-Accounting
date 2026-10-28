# -*- coding: utf-8 -*-
"""
modules/sms.py
-----------------
مدیریت ارسال پیامک به مشتریان (تکی یا گروهی).

ارسال واقعی از طریق لایه‌ی modules/sms_providers.py انجام می‌شود؛ سرویس‌دهنده
(کاوه‌نگار/ملی‌پیامک/HTTP عمومی) و مقادیرش کاملاً از تنظیمات ذخیره‌شده در
دیتابیس خوانده می‌شوند. این یعنی تعویض سرویس‌دهنده در آینده فقط نیازمند
تغییر تنظیمات از صفحه‌ی «تنظیمات → پیامک» است، نه تغییر کد.
"""

import datetime
from core.db_manager import DBManager
from modules.sms_providers import get_provider


class SMSModule:
    def __init__(self):
        self.db = DBManager.instance()

    # =================================================================
    # تنظیمات سرویس پیامک
    # =================================================================
    def get_settings(self):
        row = self.db.fetch_one("SELECT * FROM sms_settings WHERE id = 1;")
        if row is None:
            return {
                "provider": "generic",
                "api_url": "",
                "api_key": "",
                "sender_number": "",
                "http_method": "POST",
                "payload_template": "",
            }
        return {
            "provider": row["provider"] or "generic",
            "api_url": row["api_url"] or "",
            "api_key": row["api_key"] or "",
            "sender_number": row["sender_number"] or "",
            "http_method": row["http_method"] or "POST",
            "payload_template": row["payload_template"] or "",
        }

    def save_settings(self, provider, api_url, api_key, sender_number,
                       http_method="POST", payload_template=""):
        existing = self.db.fetch_one("SELECT id FROM sms_settings WHERE id = 1;")
        if existing:
            self.db.execute(
                """UPDATE sms_settings
                   SET provider = ?, api_url = ?, api_key = ?, sender_number = ?,
                       http_method = ?, payload_template = ?
                   WHERE id = 1;""",
                (provider, api_url, api_key, sender_number, http_method, payload_template),
            )
        else:
            self.db.execute(
                """INSERT INTO sms_settings
                   (id, provider, api_url, api_key, sender_number, http_method, payload_template)
                   VALUES (1, ?, ?, ?, ?, ?, ?);""",
                (provider, api_url, api_key, sender_number, http_method, payload_template),
            )

    # =================================================================
    # ارسال پیامک
    # =================================================================
    def send_sms(self, phone: str, message: str, user_id=None):
        """
        ارسال واقعی یک پیامک از طریق سرویس‌دهنده‌ی پیکربندی‌شده.
        نتیجه (موفق/ناموفق/پیکربندی‌نشده) همیشه در sms_log ثبت می‌شود.
        """
        settings = self.get_settings()
        provider = get_provider(settings["provider"])
        result = provider.send(phone, message, settings)

        sent_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.execute(
            """INSERT INTO sms_log (phone, message, status, response_snippet, sent_at, user_id)
               VALUES (?, ?, ?, ?, ?, ?);""",
            (phone, message, result["status"], result.get("response_snippet", ""), sent_at, user_id),
        )
        return result["status"]

    def send_bulk(self, recipients: list, message: str, user_id=None):
        """
        ارسال یک پیام به لیستی از گیرندگان.
        recipients: لیستی از دیکشنری‌های {name, phone}
        بازگشت: لیست نتایج [(name, phone, status), ...]
        """
        results = []
        for r in recipients:
            phone = r.get("phone")
            if not phone:
                continue
            status = self.send_sms(phone, message, user_id)
            results.append((r.get("name", ""), phone, status))
        return results

    def get_log(self, limit=200):
        return self.db.fetch_all(
            "SELECT * FROM sms_log ORDER BY id DESC LIMIT ?;", (limit,)
        )
