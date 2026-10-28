# -*- coding: utf-8 -*-
"""
ui/about_page.py
-------------------
صفحه‌ی «درباره» شامل معرفی کوتاه برنامه و اطلاعات تماس سازنده
(نام، ایمیل، واتساپ). ایمیل و واتساپ به‌صورت لینک قابل‌کلیک نمایش داده می‌شوند.
این صفحه از core/i18n.py پشتیبانی می‌کند و متد retranslate_ui() دارد.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

from core.i18n import tr

# اطلاعات تماس سازنده. این‌ها «داده» هستند نه متن رابط کاربری، پس ترجمه نمی‌شوند.
DEVELOPER_NAME = "Omid-Rezapour"
DEVELOPER_EMAIL = "rastin18241@gmail.com"
DEVELOPER_WHATSAPP_DISPLAY = "+98-930-386-9711"
# لینک واتساپ باید فقط ارقام (با کد کشور و بدون + و خط تیره) باشد.
DEVELOPER_WHATSAPP_LINK_NUMBER = "989303869711"


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        self.title = QLabel()
        self.title.setObjectName("pageTitle")
        layout.addWidget(self.title)

        self.lbl_description = QLabel()
        self.lbl_description.setWordWrap(True)
        layout.addWidget(self.lbl_description)
        layout.addSpacing(16)

        # ------------- کارت اطلاعات تماس -------------
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: #1a3a52; border-radius: 10px; }"
            "QLabel { background: transparent; color: #ffffff; font-size: 14px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(12)

        self.lbl_contact_title = QLabel()
        self.lbl_contact_title.setStyleSheet("color: #d4af37; font-size: 16px; font-weight: bold;")
        card_layout.addWidget(self.lbl_contact_title)

        self.lbl_developer_label = QLabel()
        self.lbl_developer_value = QLabel(DEVELOPER_NAME)
        self.lbl_developer_value.setStyleSheet("font-weight: bold;")
        card_layout.addLayout(self._make_row(self.lbl_developer_label, self.lbl_developer_value))

        self.lbl_email_label = QLabel()
        self.lbl_email_value = QLabel(
            f'<a href="mailto:{DEVELOPER_EMAIL}" style="color: #d4af37;">{DEVELOPER_EMAIL}</a>'
        )
        self.lbl_email_value.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_email_value.setOpenExternalLinks(True)
        card_layout.addLayout(self._make_row(self.lbl_email_label, self.lbl_email_value))

        self.lbl_whatsapp_label = QLabel()
        self.lbl_whatsapp_value = QLabel(
            f'<a href="https://wa.me/{DEVELOPER_WHATSAPP_LINK_NUMBER}" style="color: #d4af37;">'
            f"{DEVELOPER_WHATSAPP_DISPLAY}</a>"
        )
        self.lbl_whatsapp_value.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_whatsapp_value.setOpenExternalLinks(True)
        card_layout.addLayout(self._make_row(self.lbl_whatsapp_label, self.lbl_whatsapp_value))

        layout.addWidget(card)

        self.lbl_hint = QLabel()
        self.lbl_hint.setWordWrap(True)
        self.lbl_hint.setStyleSheet("color: #666666; font-size: 12px;")
        layout.addSpacing(8)
        layout.addWidget(self.lbl_hint)

        layout.addStretch()

    @staticmethod
    def _make_row(label_widget, value_widget):
        row = QHBoxLayout()
        row.addWidget(label_widget)
        row.addWidget(value_widget)
        row.addStretch()
        return row

    def retranslate_ui(self):
        self.title.setText(tr("about_page_title"))
        self.lbl_description.setText(tr("about_app_description"))
        self.lbl_contact_title.setText(tr("about_contact_title"))
        self.lbl_developer_label.setText(tr("about_developer_label"))
        self.lbl_email_label.setText(tr("about_email_label"))
        self.lbl_whatsapp_label.setText(tr("about_whatsapp_label"))
        self.lbl_hint.setText(tr("about_contact_hint"))
