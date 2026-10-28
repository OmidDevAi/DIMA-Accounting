# -*- coding: utf-8 -*-
"""
ui/dashboard_page.py
----------------------
صفحه داشبورد: نمایش خلاصه وضعیت صندوق فعال، تعداد کالاهای کم‌موجود و آخرین فاکتورها.
این صفحه از core/i18n.py پشتیبانی می‌کند و متد retranslate_ui() دارد که با
تغییر زبان از MainWindow صدا زده می‌شود.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt

from core.auth import AuthManager
from modules.inventory import InventoryModule
from modules.treasury import TreasuryModule
from modules.sales import SalesModule
from core.i18n import tr


class StatCard(QFrame):
    def __init__(self, title, value, color="#1a3a52"):
        super().__init__()
        self.setStyleSheet(
            f"QFrame {{ background-color: {color}; border-radius: 10px; }}"
        )
        self.setMinimumHeight(100)
        layout = QVBoxLayout(self)
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #d4af37; font-size: 13px; font-weight: bold;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.lbl_value = QLabel(str(value))
        self.lbl_value.setStyleSheet("color: #ffffff; font-size: 22px; font-weight: bold;")
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)

    def set_title(self, title):
        self.lbl_title.setText(title)

    def set_value(self, value):
        self.lbl_value.setText(str(value))


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self.inventory = InventoryModule()
        self.treasury = TreasuryModule()
        self.sales = SalesModule()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        self.title = QLabel()
        self.title.setObjectName("pageTitle")
        layout.addWidget(self.title)

        grid = QGridLayout()
        grid.setSpacing(16)

        box_id = self.auth.get_accessible_box_id()

        low_stock_count = len(self.inventory.get_low_stock_products())
        sale_count = len(self.sales.get_sale_invoices(box_id))
        box_balance = self.treasury.get_box_balance(box_id) if box_id is not None else tr("dashboard_all_boxes")

        self.card_sales = StatCard(tr("dashboard_sales_count"), sale_count)
        self.card_low_stock = StatCard(tr("dashboard_low_stock"), low_stock_count, color="#b23b3b")
        self.card_box_balance = StatCard(tr("dashboard_box_balance"), box_balance)

        grid.addWidget(self.card_sales, 0, 0)
        grid.addWidget(self.card_low_stock, 0, 1)
        grid.addWidget(self.card_box_balance, 0, 2)

        layout.addLayout(grid)
        layout.addStretch()

        self.retranslate_ui()

    def retranslate_ui(self):
        """به‌روزرسانی متن‌های این صفحه طبق زبان جاری؛ از MainWindow صدا زده می‌شود."""
        user = self.auth.current_user
        self.title.setText(tr("dashboard_welcome", name=user["full_name"]))
        self.card_sales.set_title(tr("dashboard_sales_count"))
        self.card_low_stock.set_title(tr("dashboard_low_stock"))
        self.card_box_balance.set_title(tr("dashboard_box_balance"))

        # مقدار کارت «مانده صندوق» وقتی ادمین است یک متن ترجمه‌شده («همه صندوق‌ها»)
        # است، نه فقط عددی که ترجمه لازم نداشته باشد؛ پس باید هر بار که زبان
        # عوض می‌شود، دوباره محاسبه و در خودِ کارت جایگزین شود.
        box_id = self.auth.get_accessible_box_id()
        box_balance = self.treasury.get_box_balance(box_id) if box_id is not None else tr("dashboard_all_boxes")
        self.card_box_balance.set_value(box_balance)
