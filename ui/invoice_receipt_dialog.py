# -*- coding: utf-8 -*-
"""
ui/invoice_receipt_dialog.py
-------------------------------
پنجره‌ی جدید (رسید فاکتور) که بلافاصله بعد از ثبت موفق هر فاکتور فروش یا خرید
باز می‌شود؛ خلاصه‌ی اقلام و مبلغ نهایی را نمایش می‌دهد و آماده‌ی چاپ است.
این پنجره از core/i18n.py پشتیبانی می‌کند.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton
)
from PyQt6.QtCore import Qt

from core.i18n import tr


class InvoiceReceiptDialog(QDialog):
    def __init__(self, parent, invoice_type_label, invoice_number, items, total_amount):
        """
        invoice_type_label: مثلاً "فاکتور فروش" یا "فاکتور خرید" (از قبل ترجمه‌شده توسط صدازننده)
        items: لیستی از دیکشنری با کلیدهای name, qty_num, price
        """
        super().__init__(parent)
        self.setWindowTitle(f"{invoice_type_label} - {invoice_number}")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(480, 520)
        self._build_ui(invoice_type_label, invoice_number, items, total_amount)

    def _build_ui(self, invoice_type_label, invoice_number, items, total_amount):
        layout = QVBoxLayout(self)

        title = QLabel(invoice_type_label)
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        lbl_number = QLabel(tr("receipt_invoice_number_label", number=invoice_number))
        layout.addWidget(lbl_number)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels([
            tr("receipt_col_name"), tr("receipt_col_qty"), tr("receipt_col_price"),
        ])
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setRowCount(len(items))
        for row_idx, item in enumerate(items):
            table.setItem(row_idx, 0, QTableWidgetItem(item.get("name", "")))
            table.setItem(row_idx, 1, QTableWidgetItem(str(item.get("qty_num", 0))))
            table.setItem(row_idx, 2, QTableWidgetItem(f"{item.get('price', 0):,.0f}"))
        layout.addWidget(table)

        lbl_total = QLabel(tr("receipt_total_label", amount=f"{total_amount:,.0f}"))
        lbl_total.setStyleSheet("font-weight: bold; font-size: 16px; color: #1a3a52;")
        layout.addWidget(lbl_total)

        button_row = QHBoxLayout()
        btn_print = QPushButton(tr("receipt_print_btn"))
        btn_print.setObjectName("goldButton")
        # اتصال به چاپگر واقعی در نسخه‌های بعدی تکمیل می‌شود (QPrinter/QPrintDialog)
        btn_print.clicked.connect(lambda: None)

        btn_close = QPushButton(tr("close_btn"))
        btn_close.clicked.connect(self.accept)

        button_row.addWidget(btn_print)
        button_row.addWidget(btn_close)
        layout.addLayout(button_row)
