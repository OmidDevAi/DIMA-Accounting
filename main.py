# -*- coding: utf-8 -*-
"""
main.py
--------
نقطه ورود برنامه حسابداری DIMA.
مسئولیت‌ها:
    - راه‌اندازی QApplication و بارگذاری تم QSS
    - مقداردهی اولیه DBManager (که خودش دیتابیس را در صورت نیاز می‌سازد)
    - مدیریت چرخه‌ی نمایش: پنجره ورود -> پنجره اصلی -> (در صورت خروج) پنجره ورود مجدد
"""

import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from core.db_manager import DBManager
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from modules.app_settings import AppSettingsModule
from core.i18n import set_language


class Application:
    """کلاس مدیریت چرخه حیات برنامه (نمایش پنجره‌ها و انتقال بین آن‌ها)."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._load_stylesheet()

        # اطمینان از ساخته شدن دیتابیس در همان ابتدای اجرا
        DBManager.instance()

        # بازیابی آخرین زبان انتخابی کاربر از دیتابیس، تا بین اجراهای مختلف حفظ شود
        set_language(AppSettingsModule().get_language())

        self.login_window = None
        self.main_window = None

    def _load_stylesheet(self):
        # اگر برنامه توسط PyInstaller بسته‌بندی شده باشد، فایل‌های همراه (مثل style.qss)
        # در یک پوشه‌ی موقت استخراج می‌شوند که مسیرش در sys._MEIPASS ذخیره شده است.
        # در حالت عادی (اجرای مستقیم با python main.py)، همان پوشه‌ی کنار main.py استفاده می‌شود.
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        style_path = os.path.join(base_dir, "ui", "style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.app.setStyleSheet(f.read())

    def run(self):
        self.show_login()
        sys.exit(self.app.exec())

    def show_login(self):
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.show_main_window)
        self.login_window.show()

    def show_main_window(self, user_info):
        if self.login_window:
            self.login_window.close()
        self.main_window = MainWindow()
        self.main_window.logged_out.connect(self.show_login)
        self.main_window.show()


if __name__ == "__main__":
    Application().run()
