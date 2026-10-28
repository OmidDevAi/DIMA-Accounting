# -*- coding: utf-8 -*-
"""
ui/treasury_page.py
----------------------
ثبت دریافت/پرداخت نقدی متصل به صندوق فعال کاربر و نمایش تاریخچه تراکنش‌ها.
این صفحه از core/i18n.py پشتیبانی می‌کند؛ TreasuryPage متد retranslate_ui() دارد.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt

from core.auth import AuthManager
from modules.treasury import TreasuryModule
from core.i18n import tr


class TreasuryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self.treasury = TreasuryModule()
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        self.title = QLabel()
        self.title.setObjectName("pageTitle")
        layout.addWidget(self.title)

        self.lbl_balance = QLabel()
        self.lbl_balance.setStyleSheet("font-weight: bold; font-size: 16px; color: #1a3a52;")
        layout.addWidget(self.lbl_balance)

        # ------------- فرم ثبت تراکنش -------------
        form_row = QHBoxLayout()
        self.lbl_type = QLabel()
        self.cmb_type = QComboBox()
        self.cmb_type.addItem("", "receive")
        self.cmb_type.addItem("", "pay")

        self.lbl_amount = QLabel()
        self.spn_amount = QDoubleSpinBox()
        self.spn_amount.setRange(0, 1_000_000_000)
        self.spn_amount.setDecimals(0)

        self.txt_description = QLineEdit()

        self.btn_submit = QPushButton()
        self.btn_submit.setObjectName("goldButton")
        self.btn_submit.clicked.connect(self.submit_transaction)

        form_row.addWidget(self.lbl_type)
        form_row.addWidget(self.cmb_type)
        form_row.addWidget(self.lbl_amount)
        form_row.addWidget(self.spn_amount)
        form_row.addWidget(self.txt_description)
        form_row.addWidget(self.btn_submit)

        layout.addLayout(form_row)

        # ------------- جدول تاریخچه -------------
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def retranslate_ui(self):
        self.title.setText(tr("treasury_page_title"))
        self.lbl_type.setText(tr("treasury_type_label"))
        self.cmb_type.setItemText(0, tr("treasury_type_receive"))
        self.cmb_type.setItemText(1, tr("treasury_type_pay"))
        self.lbl_amount.setText(tr("treasury_amount_label"))
        self.txt_description.setPlaceholderText(tr("treasury_description_placeholder"))
        self.btn_submit.setText(tr("treasury_submit_btn"))
        self.table.setHorizontalHeaderLabels([
            tr("treasury_col_id"), tr("treasury_col_type"), tr("treasury_col_amount"),
            tr("treasury_col_date"), tr("treasury_col_description"),
        ])
        self.refresh()

    def refresh(self):
        box_id = self.auth.get_accessible_box_id()
        active_box_id = self.auth.current_user["box_id"]

        balance = self.treasury.get_box_balance(active_box_id) if active_box_id else 0
        self.lbl_balance.setText(tr("treasury_balance_label", amount=f"{balance:,.0f}"))

        transactions = self.treasury.get_transactions(box_id)
        self.table.setRowCount(0)
        for row_idx, t in enumerate(transactions):
            self.table.insertRow(row_idx)
            type_label = tr("treasury_row_receive") if t["trans_type"] == "receive" else tr("treasury_row_pay")
            values = [str(t["id"]), type_label, f"{t['amount']:,.0f}", t["date"], t["description"] or ""]
            for col_idx, val in enumerate(values):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))

    def submit_transaction(self):
        amount = self.spn_amount.value()
        if amount <= 0:
            QMessageBox.warning(self, tr("warning_title"), tr("treasury_error_amount"))
            return

        active_box_id = self.auth.current_user["box_id"]
        if active_box_id is None:
            QMessageBox.warning(self, tr("warning_title"), tr("treasury_error_no_box"))
            return

        try:
            self.treasury.register_transaction(
                trans_type=self.cmb_type.currentData(),
                amount=amount,
                box_id=active_box_id,
                user_id=self.auth.current_user["id"],
                description=self.txt_description.text().strip(),
            )
            self.spn_amount.setValue(0)
            self.txt_description.clear()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, tr("warning_title"), tr("treasury_error_submit", error=str(e)))
