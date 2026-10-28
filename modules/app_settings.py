# -*- coding: utf-8 -*-
"""
modules/app_settings.py
--------------------------
تنظیمات عمومی و سراسری برنامه که به کاربر خاصی وابسته نیست (فعلاً فقط
زبان انتخابی رابط کاربری). با این ماژول، زبان انتخابی بین اجراهای مختلف
برنامه حفظ می‌شود.
"""

from core.db_manager import DBManager


class AppSettingsModule:
    def __init__(self):
        self.db = DBManager.instance()

    def get_language(self) -> str:
        row = self.db.fetch_one("SELECT language FROM app_settings WHERE id = 1;")
        return row["language"] if row else "fa"

    def save_language(self, language_code: str):
        existing = self.db.fetch_one("SELECT id FROM app_settings WHERE id = 1;")
        if existing:
            self.db.execute("UPDATE app_settings SET language = ? WHERE id = 1;", (language_code,))
        else:
            self.db.execute("INSERT INTO app_settings (id, language) VALUES (1, ?);", (language_code,))
