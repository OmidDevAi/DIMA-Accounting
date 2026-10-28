# -*- coding: utf-8 -*-
"""
ui/invoices_page.py
----------------------
تاریخچه‌ی فاکتورهای فروش و خرید.
مشاهده برای همه‌ی نقش‌ها در دسترس است؛ حذف فاکتور فقط برای مدیر فروشگاه و
حسابدار مجاز است. این صفحه از core/i18n.py پشتیبانی می‌کند.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QHeaderView, QDialog
)
from PyQt6.QtCore import Qt

from core.auth import AuthManager
from modules.invoices import InvoiceModule
from core.i18n import tr


class InvoiceDetailsDialog(QDialog):
    """نمایش جزئیات اقلام یک فاکتور."""

    def __init__(self, parent, invoice, items):
        super().__init__(parent)
        payment_labels = {"cash": tr("payment_cash"), "credit": tr("payment_credit"), "card": tr("payment_card")}
        self.setWindowTitle(tr("invoices_details_dialog_title", number=invoice["invoice_number"]))
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(520, 420)
        self._build_ui(invoice, items, payment_labels)

    def _build_ui(self, invoice, items, payment_labels):
        layout = QVBoxLayout(self)

        header = QLabel(
            tr(
                "invoices_details_header",
                number=invoice["invoice_number"], date=invoice["date"],
                payment=payment_labels.get(invoice["payment_type"], invoice["payment_type"]),
            )
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        if invoice["party_name"]:
            layout.addWidget(QLabel(tr("invoices_details_party", name=invoice["party_name"])))

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            tr("invoices_details_col_code"), tr("invoices_details_col_name"),
            tr("invoices_details_col_qty"), tr("invoices_details_col_price"), tr("invoices_details_col_total"),
        ])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setRowCount(len(items))
        for row_idx, item in enumerate(items):
            table.setItem(row_idx, 0, QTableWidgetItem(item["product_code"]))
            table.setItem(row_idx, 1, QTableWidgetItem(item["product_name"]))
            table.setItem(row_idx, 2, QTableWidgetItem(str(item["qty_num"] + item["qty_box"])))
            table.setItem(row_idx, 3, QTableWidgetItem(f"{item['price']:,.0f}"))
            table.setItem(row_idx, 4, QTableWidgetItem(f"{item['line_total']:,.0f}"))
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)

        lbl_total = QLabel(tr("invoices_details_total", amount=f"{invoice['total_amount']:,.0f}"))
        lbl_total.setStyleSheet("font-weight: bold; font-size: 15px; color: #1a3a52;")
        layout.addWidget(lbl_total)

        btn_close = QPushButton(tr("close_btn"))
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


class InvoicesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self.invoices = InvoiceModule()
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        self.title = QLabel()
        self.title.setObjectName("pageTitle")
        layout.addWidget(self.title)

        toolbar = QHBoxLayout()
        self.lbl_type_filter = QLabel()
        self.cmb_type_filter = QComboBox()
        self.cmb_type_filter.addItem("", None)
        self.cmb_type_filter.addItem("", "sale")
        self.cmb_type_filter.addItem("", "purchase")
        self.cmb_type_filter.currentIndexChanged.connect(self.refresh)

        self.txt_search = QLineEdit()
        self.txt_search.textChanged.connect(self.refresh)

        toolbar.addWidget(self.lbl_type_filter)
        toolbar.addWidget(self.cmb_type_filter)
        toolbar.addStretch()
        toolbar.addWidget(self.txt_search)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader()
        for col in range(7):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        action_row = QHBoxLayout()
        self.btn_view = QPushButton()
        self.btn_view.setObjectName("goldButton")
        self.btn_view.clicked.connect(self.view_selected)
        action_row.addWidget(self.btn_view)

        self.btn_delete = None
        if self.auth.can_manage_products():
            self.btn_delete = QPushButton()
            self.btn_delete.setObjectName("dangerButton")
            self.btn_delete.clicked.connect(self.delete_selected)
            action_row.addWidget(self.btn_delete)

        action_row.addStretch()
        layout.addLayout(action_row)

    def retranslate_ui(self):
        self.title.setText(tr("invoices_page_title"))
        self.lbl_type_filter.setText(tr("invoices_type_filter_label"))
        self.cmb_type_filter.setItemText(0, tr("invoices_type_all"))
        self.cmb_type_filter.setItemText(1, tr("invoice_type_sale"))
        self.cmb_type_filter.setItemText(2, tr("invoice_type_purchase"))
        self.txt_search.setPlaceholderText(tr("invoices_search_placeholder"))
        self.table.setHorizontalHeaderLabels([
            tr("invoices_col_id"), tr("invoices_col_number"), tr("invoices_col_type"),
            tr("invoices_col_date"), tr("invoices_col_party"), tr("invoices_col_payment"),
            tr("invoices_col_total"), tr("invoices_col_registered_by"),
        ])
        self.btn_view.setText(tr("invoices_view_details_btn"))
        if self.btn_delete is not None:
            self.btn_delete.setText(tr("invoices_delete_btn"))
        self.refresh()

    def refresh(self):
        box_id = self.auth.get_accessible_box_id()
        invoice_type = self.cmb_type_filter.currentData()
        keyword = self.txt_search.text().strip().lower()

        rows = self.invoices.get_all_invoices(box_id, invoice_type)
        if keyword:
            rows = [
                r for r in rows
                if keyword in r["invoice_number"].lower() or keyword in (r["party_name"] or "").lower()
            ]

        invoice_type_labels = {"sale": tr("invoice_type_sale"), "purchase": tr("invoice_type_purchase")}
        payment_labels = {"cash": tr("payment_cash"), "credit": tr("payment_credit"), "card": tr("payment_card")}

        self.table.setRowCount(0)
        for row_idx, r in enumerate(rows):
            self.table.insertRow(row_idx)
            values = [
                str(r["id"]), r["invoice_number"],
                invoice_type_labels.get(r["invoice_type"], r["invoice_type"]),
                r["date"], r["party_name"] or "-",
                payment_labels.get(r["payment_type"], r["payment_type"]),
                f"{r['total_amount']:,.0f}", r["user_name"] or "-",
            ]
            for col_idx, val in enumerate(values):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))

    def _selected_invoice_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def view_selected(self):
        invoice_id = self._selected_invoice_id()
        if invoice_id is None:
            QMessageBox.information(self, tr("info_title"), tr("invoices_select_first"))
            return
        invoice = self.invoices.db.fetch_one(
            """SELECT i.*, p.name AS party_name FROM invoices i
               LEFT JOIN parties p ON i.party_id = p.id WHERE i.id = ?;""",
            (invoice_id,),
        )
        items = self.invoices.get_invoice_items(invoice_id)
        dialog = InvoiceDetailsDialog(self, invoice, items)
        dialog.exec()

    def delete_selected(self):
        invoice_id = self._selected_invoice_id()
        if invoice_id is None:
            QMessageBox.information(self, tr("info_title"), tr("invoices_select_first"))
            return

        confirm = QMessageBox.question(
            self, tr("invoices_confirm_delete_title"), tr("invoices_confirm_delete_message")
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            self.invoices.delete_invoice(invoice_id)
            QMessageBox.information(self, tr("success_title"), tr("invoices_delete_success"))
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, tr("warning_title"), tr("invoices_delete_error", error=str(e)))
