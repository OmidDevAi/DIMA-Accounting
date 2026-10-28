# -*- coding: utf-8 -*-
"""
ui/login_window.py
--------------------
پنجره ورود (Login) - نمایش اجباری قبل از دسترسی به داشبورد اصلی.
پس از ورود موفق، سیگنال login_success با اطلاعات کاربر ارسال می‌شود
تا main.py پنجره اصلی را باز کند (ارتباط غیرمستقیم Signals & Slots).

این صفحه از سازوکار چندزبانه‌ی core/i18n.py استفاده می‌کند و انتخابگر زبان
بالای پنجره قرار دارد (فارسی/English/Français/Deutsch).
"""

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QMessageBox, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.auth import AuthManager
from core.i18n import tr, set_language, get_language, get_layout_direction, SUPPORTED_LANGUAGES
from modules.app_settings import AppSettingsModule


class LoginWindow(QWidget):
    # سیگنال ورود موفق؛ دیکشنری اطلاعات کاربر را منتقل می‌کند
    login_success = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self.setFixedSize(420, 520)
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # ------------- انتخابگر زبان -------------
        lang_row = QHBoxLayout()
        lang_row.setContentsMargins(12, 8, 12, 0)
        self.lbl_language = QLabel()
        self.cmb_language = QComboBox()
        for code, info in SUPPORTED_LANGUAGES.items():
            self.cmb_language.addItem(info["label"], code)
        idx = self.cmb_language.findData(get_language())
        if idx >= 0:
            self.cmb_language.setCurrentIndex(idx)
        self.cmb_language.currentIndexChanged.connect(self.change_language)
        lang_row.addWidget(self.lbl_language)
        lang_row.addWidget(self.cmb_language)
        lang_row.addStretch()
        outer.addLayout(lang_row)

        # ------------- هدر برند -------------
        header = QFrame()
        header.setObjectName("loginHeader")
        header.setStyleSheet("background-color: #1a3a52;")
        header.setFixedHeight(140)
        header_layout = QVBoxLayout(header)

        self.lbl_title = QLabel()
        self.lbl_title.setStyleSheet("color: #d4af37; font-size: 20px; font-weight: bold;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_subtitle = QLabel()
        self.lbl_subtitle.setStyleSheet("color: #ffffff; font-size: 12px;")
        self.lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addStretch()
        header_layout.addWidget(self.lbl_title)
        header_layout.addWidget(self.lbl_subtitle)
        header_layout.addStretch()

        outer.addWidget(header)

        # ------------- فرم ورود -------------
        form_container = QVBoxLayout()
        form_container.setContentsMargins(40, 30, 40, 30)
        form_container.setSpacing(14)

        self.lbl_user = QLabel()
        self.txt_username = QLineEdit()

        self.lbl_pass = QLabel()
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.returnPressed.connect(self.handle_login)

        self.btn_login = QPushButton()
        self.btn_login.setObjectName("goldButton")
        self.btn_login.setMinimumHeight(42)
        self.btn_login.clicked.connect(self.handle_login)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #b23b3b; font-weight: bold;")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_container.addWidget(self.lbl_user)
        form_container.addWidget(self.txt_username)
        form_container.addWidget(self.lbl_pass)
        form_container.addWidget(self.txt_password)
        form_container.addSpacing(10)
        form_container.addWidget(self.btn_login)
        form_container.addWidget(self.lbl_error)
        form_container.addStretch()

        self.lbl_hint = QLabel()
        self.lbl_hint.setStyleSheet("color: #888888; font-size: 11px;")
        self.lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_container.addWidget(self.lbl_hint)

        outer.addLayout(form_container)

    # ---------------------------------------------------------------
    def change_language(self):
        """تغییر زبان جاری برنامه، ذخیره‌ی دائمی آن، و به‌روزرسانی فوری تمام متن‌های همین صفحه."""
        language_code = self.cmb_language.currentData()
        set_language(language_code)
        AppSettingsModule().save_language(language_code)
        self.retranslate_ui()

    def retranslate_ui(self):
        """بازنویسی تمام متن‌های قابل‌مشاهده طبق زبان جاری."""
        direction = get_layout_direction()
        self.setLayoutDirection(direction)

        self.setWindowTitle(tr("app_title"))
        self.lbl_language.setText(tr("language_label"))
        self.lbl_title.setText(tr("app_title"))
        self.lbl_subtitle.setText(tr("login_subtitle"))
        self.lbl_user.setText(tr("login_username_label"))
        self.txt_username.setPlaceholderText(tr("login_username_placeholder"))
        self.lbl_pass.setText(tr("login_password_label"))
        self.txt_password.setPlaceholderText(tr("login_password_placeholder"))
        self.btn_login.setText(tr("login_button"))
        self.lbl_hint.setText(tr("login_hint"))

    def handle_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()

        if not username or not password:
            self.lbl_error.setText(tr("login_error_empty"))
            return

        user = self.auth.login(username, password)
        if user is None:
            self.lbl_error.setText(tr("login_error_invalid"))
            self.txt_password.clear()
            return

        self.lbl_error.setText("")
        self.login_success.emit(user)
