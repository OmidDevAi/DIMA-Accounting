# -*- coding: utf-8 -*-
"""
ui/customers_page.py
----------------------
لیست و جستجوی مشتریان + تاریخچه‌ی فاکتور یک‌سال‌اخیر + ارسال پیامک.
این صفحه از core/i18n.py پشتیبانی می‌کند؛ CustomersPage متد retranslate_ui() دارد
که همه‌ی تب‌ها را هم به‌روزرسانی می‌کند.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QDialog,
    QFormLayout, QTabWidget, QTextEdit, QDateEdit
)
from PyQt6.QtCore import Qt, QDate

from core.auth import AuthManager
from modules.customers import CustomerModule
from modules.sms import SMSModule
from core.i18n import tr


class AddCustomerDialog(QDialog):
    """فرم افزودن دستی مشتری جدید (فقط نام و شماره موبایل)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("customers_add_dialog_title"))
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        form = QFormLayout(self)

        self.txt_name = QLineEdit()
        self.txt_phone = QLineEdit()
        form.addRow(tr("customers_name_label"), self.txt_name)
        form.addRow(tr("customers_phone_label"), self.txt_phone)

        btn_save = QPushButton(tr("save_btn"))
        btn_save.setObjectName("saveButton")
        btn_save.clicked.connect(self.accept)
        form.addRow(btn_save)

    def get_data(self):
        return self.txt_name.text().strip(), self.txt_phone.text().strip()


class SMSComposeDialog(QDialog):
    """دیالوگ نوشتن و ارسال پیامک؛ هم برای ارسال تکی و هم گروهی استفاده می‌شود."""

    def __init__(self, parent, recipients: list, sms_module: SMSModule, user_id):
        super().__init__(parent)
        self.recipients = recipients
        self.sms = sms_module
        self.user_id = user_id
        self.setWindowTitle(tr("sms_compose_dialog_title"))
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(420, 320)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        lbl_count = QLabel(tr("sms_recipients_count", n=len(self.recipients)))
        lbl_count.setStyleSheet("font-weight: bold; color: #1a3a52;")
        layout.addWidget(lbl_count)

        names_preview = "، ".join(r["name"] for r in self.recipients[:5])
        if len(self.recipients) > 5:
            names_preview += " " + tr("sms_names_more", n=len(self.recipients) - 5)
        lbl_names = QLabel(names_preview)
        lbl_names.setWordWrap(True)
        lbl_names.setStyleSheet("color: #666666; font-size: 12px;")
        layout.addWidget(lbl_names)

        self.txt_message = QTextEdit()
        self.txt_message.setPlaceholderText(tr("sms_message_placeholder"))
        layout.addWidget(self.txt_message)

        btn_send = QPushButton(tr("sms_send_btn"))
        btn_send.setObjectName("goldButton")
        btn_send.clicked.connect(self.send)
        layout.addWidget(btn_send)

    def send(self):
        message = self.txt_message.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, tr("warning_title"), tr("sms_error_empty_message"))
            return
        if not self.recipients:
            QMessageBox.information(self, tr("info_title"), tr("sms_error_no_recipients"))
            return

        results = self.sms.send_bulk(self.recipients, message, self.user_id)
        sent = sum(1 for _, _, status in results if status == "sent")
        not_configured = sum(1 for _, _, status in results if status == "not_configured")
        failed = sum(1 for _, _, status in results if status in ("failed", "error", "invalid_template"))
        no_requests_lib = sum(1 for _, _, status in results if status == "requests_not_installed")

        summary = tr("sms_result_summary", total=len(results), sent=sent)
        if not_configured:
            summary += "\n" + tr("sms_result_not_configured", n=not_configured)
        if failed:
            summary += "\n" + tr("sms_result_failed", n=failed)
        if no_requests_lib:
            summary += "\n" + tr("sms_result_no_requests_lib", n=no_requests_lib)
        QMessageBox.information(self, tr("sms_result_title"), summary)
        self.accept()


class CustomerListTab(QWidget):
    """لیست/جستجوی مشتریان + تاریخچه خرید + پیامک تکی به یک مشتری."""

    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self.customers = CustomerModule()
        self.sms = SMSModule()
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.textChanged.connect(self.refresh_list)

        self.btn_add = QPushButton()
        self.btn_add.setObjectName("goldButton")
        self.btn_add.clicked.connect(self.add_customer)

        toolbar.addWidget(self.btn_add)
        toolbar.addStretch()
        toolbar.addWidget(self.txt_search)
        layout.addLayout(toolbar)

        body = QHBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader()
        for col in range(3):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.itemSelectionChanged.connect(self.show_customer_invoices)
        body.addWidget(self.table, 1)

        right_panel = QVBoxLayout()
        self.lbl_history_title = QLabel()
        self.lbl_history_title.setStyleSheet("font-weight: bold; color: #1a3a52;")
        self.lbl_history_title.setWordWrap(True)
        right_panel.addWidget(self.lbl_history_title)

        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(4)
        self.invoice_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        invoice_header = self.invoice_table.horizontalHeader()
        for col in range(3):
            invoice_header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        invoice_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        right_panel.addWidget(self.invoice_table)

        self.btn_sms_one = QPushButton()
        self.btn_sms_one.setObjectName("goldButton")
        self.btn_sms_one.clicked.connect(self.send_sms_to_selected)
        right_panel.addWidget(self.btn_sms_one)

        body.addLayout(right_panel, 1)
        layout.addLayout(body)

    def retranslate_ui(self):
        self.txt_search.setPlaceholderText(tr("customers_search_placeholder"))
        self.btn_add.setText(tr("customers_add_btn"))
        self.table.setHorizontalHeaderLabels([
            tr("customers_col_id"), tr("customers_col_name"),
            tr("customers_col_phone"), tr("customers_col_balance"),
        ])
        self.invoice_table.setHorizontalHeaderLabels([
            tr("customers_invoice_col_number"), tr("customers_invoice_col_date"),
            tr("customers_invoice_col_payment"), tr("customers_invoice_col_total"),
        ])
        self.btn_sms_one.setText(tr("customers_sms_to_selected_btn"))
        if self.table.currentRow() < 0:
            self.lbl_history_title.setText(tr("customers_history_placeholder"))
        self.refresh_list()

    def refresh_list(self):
        keyword = self.txt_search.text().strip()
        customers = self.customers.search_customers(keyword) if keyword else self.customers.get_all_customers()
        self.table.setRowCount(0)
        for row_idx, c in enumerate(customers):
            self.table.insertRow(row_idx)
            values = [str(c["id"]), c["name"], c["phone"] or "-", f"{c['balance']:,.0f}"]
            for col_idx, val in enumerate(values):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))

    def add_customer(self):
        dialog = AddCustomerDialog(self)
        if dialog.exec():
            name, phone = dialog.get_data()
            if not name or not phone:
                QMessageBox.warning(self, tr("warning_title"), tr("customers_error_both_required"))
                return
            if self.customers.find_by_phone(phone):
                QMessageBox.warning(self, tr("warning_title"), tr("customers_error_duplicate_phone"))
                return
            self.customers.create_customer(name, phone)
            self.refresh_list()

    def _selected_customer(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return {
            "id": int(self.table.item(row, 0).text()),
            "name": self.table.item(row, 1).text(),
            "phone": self.table.item(row, 2).text(),
        }

    def show_customer_invoices(self):
        customer = self._selected_customer()
        if customer is None:
            return
        self.lbl_history_title.setText(tr("customers_history_title", name=customer["name"]))

        invoices = self.customers.get_customer_invoices(customer["id"])
        payment_labels = {"cash": tr("payment_cash"), "credit": tr("payment_credit"), "card": tr("payment_card")}

        self.invoice_table.setRowCount(0)
        for row_idx, inv in enumerate(invoices):
            self.invoice_table.insertRow(row_idx)
            values = [
                inv["invoice_number"], inv["date"],
                payment_labels.get(inv["payment_type"], inv["payment_type"]),
                f"{inv['total_amount']:,.0f}",
            ]
            for col_idx, val in enumerate(values):
                self.invoice_table.setItem(row_idx, col_idx, QTableWidgetItem(val))

    def send_sms_to_selected(self):
        customer = self._selected_customer()
        if customer is None:
            QMessageBox.information(self, tr("info_title"), tr("customers_select_first"))
            return
        if customer["phone"] in ("", "-"):
            QMessageBox.warning(self, tr("warning_title"), tr("customers_error_no_phone"))
            return
        dialog = SMSComposeDialog(self, [customer], self.sms, self.auth.current_user["id"])
        dialog.exec()


class BulkSMSTab(QWidget):
    """پیامک گروهی به کل لیست مشتریان؛ فقط مدیر فروشگاه و حسابدار."""

    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self.customers = CustomerModule()
        self.sms = SMSModule()
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        if not self.auth.can_send_bulk_sms():
            self.lbl_denied = QLabel()
            self.lbl_denied.setWordWrap(True)
            layout.addWidget(self.lbl_denied)
            return

        self.lbl_info = QLabel()
        self.lbl_info.setWordWrap(True)
        layout.addWidget(self.lbl_info)

        self.lbl_total_customers = QLabel("")
        self.lbl_total_customers.setStyleSheet("font-weight: bold; color: #1a3a52;")
        layout.addWidget(self.lbl_total_customers)

        self.btn_open_compose = QPushButton()
        self.btn_open_compose.setObjectName("goldButton")
        self.btn_open_compose.clicked.connect(self.open_compose)
        layout.addWidget(self.btn_open_compose)
        layout.addStretch()

    def retranslate_ui(self):
        if not self.auth.can_send_bulk_sms():
            self.lbl_denied.setText(tr("customers_bulk_access_denied"))
            return
        self.lbl_info.setText(tr("customers_bulk_info"))
        self.btn_open_compose.setText(tr("customers_bulk_compose_btn"))
        self._refresh_count()

    def _refresh_count(self):
        count = len(self.customers.get_all_customers())
        self.lbl_total_customers.setText(tr("customers_total_count", n=count))

    def open_compose(self):
        all_customers = self.customers.get_all_customers()
        recipients = [
            {"name": c["name"], "phone": c["phone"]} for c in all_customers if c["phone"]
        ]
        if not recipients:
            QMessageBox.information(self, tr("info_title"), tr("customers_no_phone_customers"))
            return
        dialog = SMSComposeDialog(self, recipients, self.sms, self.auth.current_user["id"])
        dialog.exec()


class InactiveCustomersTab(QWidget):
    """جستجوی مشتریانی که در یک بازه خرید نکرده‌اند + پیامک به آن‌ها؛ فقط مدیر فروشگاه و صندوق‌دار."""

    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self.customers = CustomerModule()
        self.sms = SMSModule()
        self.found_customers = []
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        if not self.auth.can_search_inactive_customers():
            self.lbl_denied = QLabel()
            self.lbl_denied.setWordWrap(True)
            layout.addWidget(self.lbl_denied)
            return

        self.lbl_info = QLabel()
        self.lbl_info.setWordWrap(True)
        layout.addWidget(self.lbl_info)

        date_row = QHBoxLayout()
        self.date_from = QDateEdit(QDate.currentDate().addMonths(-3))
        self.date_from.setCalendarPopup(True)
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.btn_search = QPushButton()
        self.btn_search.setObjectName("goldButton")
        self.btn_search.clicked.connect(self.search)

        self.lbl_date_from = QLabel()
        self.lbl_date_to = QLabel()
        date_row.addWidget(self.lbl_date_from)
        date_row.addWidget(self.date_from)
        date_row.addWidget(self.lbl_date_to)
        date_row.addWidget(self.date_to)
        date_row.addWidget(self.btn_search)
        layout.addLayout(date_row)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader()
        for col in range(2):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self.btn_sms_all = QPushButton()
        self.btn_sms_all.setObjectName("goldButton")
        self.btn_sms_all.clicked.connect(self.send_sms_to_all_found)
        layout.addWidget(self.btn_sms_all)

    def retranslate_ui(self):
        if not self.auth.can_search_inactive_customers():
            self.lbl_denied.setText(tr("customers_inactive_access_denied"))
            return
        self.lbl_info.setText(tr("customers_inactive_info"))
        self.lbl_date_from.setText(tr("customers_date_from_label"))
        self.lbl_date_to.setText(tr("customers_date_to_label"))
        self.btn_search.setText(tr("search_btn"))
        self.table.setHorizontalHeaderLabels([
            tr("customers_col_id"), tr("customers_col_name"), tr("customers_col_phone"),
        ])
        self.btn_sms_all.setText(tr("customers_sms_to_all_found_btn"))

    def search(self):
        date_from = self.date_from.date().toString("yyyyMMdd")
        date_to = self.date_to.date().toString("yyyyMMdd")
        self.found_customers = self.customers.find_inactive_customers(date_from, date_to)

        self.table.setRowCount(0)
        for row_idx, c in enumerate(self.found_customers):
            self.table.insertRow(row_idx)
            values = [str(c["id"]), c["name"], c["phone"] or "-"]
            for col_idx, val in enumerate(values):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))

    def send_sms_to_all_found(self):
        if not self.found_customers:
            QMessageBox.information(self, tr("info_title"), tr("customers_search_first"))
            return
        recipients = [
            {"name": c["name"], "phone": c["phone"]} for c in self.found_customers if c["phone"]
        ]
        if not recipients:
            QMessageBox.information(self, tr("info_title"), tr("customers_no_phone_results"))
            return
        dialog = SMSComposeDialog(self, recipients, self.sms, self.auth.current_user["id"])
        dialog.exec()


class CustomersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        self.title = QLabel()
        self.title.setObjectName("pageTitle")
        layout.addWidget(self.title)

        self.tabs = QTabWidget()
        self.tab_list = CustomerListTab()
        self.tabs.addTab(self.tab_list, "")

        self.tab_bulk = None
        self.tab_inactive = None
        if self.auth.can_send_bulk_sms():
            self.tab_bulk = BulkSMSTab()
            self.tabs.addTab(self.tab_bulk, "")
        if self.auth.can_search_inactive_customers():
            self.tab_inactive = InactiveCustomersTab()
            self.tabs.addTab(self.tab_inactive, "")

        layout.addWidget(self.tabs)

    def retranslate_ui(self):
        self.title.setText(tr("customers_page_title"))
        index = 0
        self.tabs.setTabText(index, tr("customers_tab_list"))
        self.tab_list.retranslate_ui()
        index += 1
        if self.tab_bulk is not None:
            self.tabs.setTabText(index, tr("customers_tab_bulk_sms"))
            self.tab_bulk.retranslate_ui()
            index += 1
        if self.tab_inactive is not None:
            self.tabs.setTabText(index, tr("customers_tab_inactive"))
            self.tab_inactive.retranslate_ui()
