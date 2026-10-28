# -*- coding: utf-8 -*-
"""
modules/scanner_settings.py
------------------------------
ذخیره و بازیابی تنظیمات دستگاه بارکدخوان (نوع اتصال، پورت سریال، Baud Rate).
"""

from core.db_manager import DBManager


class ScannerSettingsModule:
    def __init__(self):
        self.db = DBManager.instance()

    def get_settings(self):
        row = self.db.fetch_one("SELECT * FROM scanner_settings WHERE id = 1;")
        if row is None:
            return {"mode": "usb", "port": "", "baud_rate": 9600}
        return {
            "mode": row["mode"],
            "port": row["port"] or "",
            "baud_rate": row["baud_rate"],
        }

    def save_settings(self, mode, port, baud_rate):
        existing = self.db.fetch_one("SELECT id FROM scanner_settings WHERE id = 1;")
        if existing:
            self.db.execute(
                "UPDATE scanner_settings SET mode = ?, port = ?, baud_rate = ? WHERE id = 1;",
                (mode, port, baud_rate),
            )
        else:
            self.db.execute(
                "INSERT INTO scanner_settings (id, mode, port, baud_rate) VALUES (1, ?, ?, ?);",
                (mode, port, baud_rate),
            )
