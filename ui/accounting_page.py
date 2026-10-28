# -*- coding: utf-8 -*-
"""
ui/accounting_page.py
------------------------
صفحه حسابداری کامل، فقط برای مدیر فروشگاه و حسابدار در دسترس است.
شامل تب‌های: سرفصل حسابها، صدور سند، دفتر کل، تراز آزمایشی، سود و زیان،
ترازنامه، و اسناد ارسال به سامانه مودیان.
این صفحه از core/i18n.py پشتیبانی می‌کند؛ AccountingPage.retranslate_ui() همه‌ی
تب‌ها را هم به‌روزرسانی می‌کند.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QTabWidget, QDateEdit, QTextEdit
)
from PyQt6.QtCore import Qt, QDate

from core.auth import AuthManager
from modules.accounting import AccountingModule
from modules.modian import ModianModule
from core.i18n import tr


ACCOUNT_TYPE_KEYS = {
    "asset": "account_type_asset",
    "liability": "account_type_liability",
    "equity": "account_type_equity",
    "revenue": "account_type_revenue",
    "expense": "account_type_expense",
}


class ChartOfAccountsTab(QWidget):
    def __init__(self, accounting: AccountingModule):
        super().__init__()
        self.accounting = accounting
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form_row = QHBoxLayout()

        self.txt_code = QLineEdit()
        self.txt_name = QLineEdit()
        self.cmb_type = QComboBox()
        for key in ACCOUNT_TYPE_KEYS:
            self.cmb_type.addItem("", key)

        self.btn_add = QPushButton()
        self.btn_add.setObjectName("goldButton")
        self.btn_add.clicked.connect(self.add_account)

        form_row.addWidget(self.txt_code)
        form_row.addWidget(self.txt_name)
        form_row.addWidget(self.cmb_type)
        form_row.addWidget(self.btn_add)
        layout.addLayout(form_row)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def retranslate_ui(self):
        self.txt_code.setPlaceholderText(tr("accounting_code_placeholder"))
        self.txt_name.setPlaceholderText(tr("accounting_name_placeholder"))
        for idx, key in enumerate(ACCOUNT_TYPE_KEYS):
            self.cmb_type.setItemText(idx, tr(ACCOUNT_TYPE_KEYS[key]))
        self.btn_add.setText(tr("accounting_add_account_btn"))
        self.table.setHorizontalHeaderLabels([
            tr("accounting_col_code"), tr("accounting_col_account_name"), tr("accounting_col_type"),
        ])
        self.refresh()

    def refresh(self):
        accounts = self.accounting.get_accounts()
        self.table.setRowCount(0)
        for row_idx, a in enumerate(accounts):
            self.table.insertRow(row_idx)
            type_label = tr(ACCOUNT_TYPE_KEYS.get(a["account_type"], ""))
            values = [a["code"], a["name"], type_label]
            for col_idx, val in enumerate(values):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))

    def add_account(self):
        code = self.txt_code.text().strip()
        name = self.txt_name.text().strip()
        if not code or not name:
            QMessageBox.warning(self, tr("warning_title"), tr("accounting_error_code_name_required"))
            return
        try:
            self.accounting.add_account(code, name, self.cmb_type.currentData())
            self.txt_code.clear()
            self.txt_name.clear()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, tr("warning_title"), tr("accounting_error_add_account", error=str(e)))


class JournalEntryTab(QWidget):
    """صدور سند حسابداری دستی؛ باید مجموع بدهکار و بستانکار برابر باشد."""

    def __init__(self, accounting: AccountingModule, current_user):
        super().__init__()
        self.accounting = accounting
        self.current_user = current_user
        self.entry_lines = []
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.txt_description = QLineEdit()
        layout.addWidget(self.txt_description)

        add_row = QHBoxLayout()
        self.cmb_account = QComboBox()
        for a in self.accounting.get_accounts():
            self.cmb_account.addItem(f"{a['code']} - {a['name']}", a["id"])
        self.spn_debit = QDoubleSpinBox()
        self.spn_debit.setRange(0, 1_000_000_000)
        self.spn_debit.setDecimals(0)
        self.spn_credit = QDoubleSpinBox()
        self.spn_credit.setRange(0, 1_000_000_000)
        self.spn_credit.setDecimals(0)
        self.btn_add_line = QPushButton()
        self.btn_add_line.clicked.connect(self.add_line)

        self.lbl_account = QLabel()
        self.lbl_debit = QLabel()
        self.lbl_credit = QLabel()
        add_row.addWidget(self.lbl_account)
        add_row.addWidget(self.cmb_account)
        add_row.addWidget(self.lbl_debit)
        add_row.addWidget(self.spn_debit)
        add_row.addWidget(self.lbl_credit)
        add_row.addWidget(self.spn_credit)
        add_row.addWidget(self.btn_add_line)
        layout.addLayout(add_row)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        bottom_row = QHBoxLayout()
        self.lbl_balance = QLabel()
        self.lbl_balance.setStyleSheet("font-weight: bold; color: #1a3a52;")
        self.btn_submit = QPushButton()
        self.btn_submit.setObjectName("goldButton")
        self.btn_submit.clicked.connect(self.submit_entry)
        bottom_row.addWidget(self.lbl_balance)
        bottom_row.addStretch()
        bottom_row.addWidget(self.btn_submit)
        layout.addLayout(bottom_row)

    def retranslate_ui(self):
        self.txt_description.setPlaceholderText(tr("accounting_description_placeholder"))
        self.lbl_account.setText(tr("accounting_account_label"))
        self.lbl_debit.setText(tr("accounting_debit_label"))
        self.lbl_credit.setText(tr("accounting_credit_label"))
        self.btn_add_line.setText(tr("accounting_add_line_btn"))
        self.table.setHorizontalHeaderLabels([
            tr("accounting_account_label").rstrip(":"), tr("accounting_debit_label").rstrip(":"),
            tr("accounting_credit_label").rstrip(":"),
        ])
        self.btn_submit.setText(tr("accounting_submit_entry_btn"))
        self._render_lines()

    def add_line(self):
        debit = self.spn_debit.value()
        credit = self.spn_credit.value()
        if debit == 0 and credit == 0:
            QMessageBox.warning(self, tr("warning_title"), tr("accounting_error_line_amount"))
            return
        if debit > 0 and credit > 0:
            QMessageBox.warning(self, tr("warning_title"), tr("accounting_error_line_both"))
            return

        self.entry_lines.append({
            "account_id": self.cmb_account.currentData(),
            "account_label": self.cmb_account.currentText(),
            "debit": debit,
            "credit": credit,
        })
        self.spn_debit.setValue(0)
        self.spn_credit.setValue(0)
        self._render_lines()

    def _render_lines(self):
        self.table.setRowCount(0)
        total_debit = 0
        total_credit = 0
        for row_idx, line in enumerate(self.entry_lines):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(line["account_label"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(f"{line['debit']:,.0f}"))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{line['credit']:,.0f}"))
            total_debit += line["debit"]
            total_credit += line["credit"]
        self.lbl_balance.setText(tr("accounting_balance_label", debit=f"{total_debit:,.0f}", credit=f"{total_credit:,.0f}"))

    def submit_entry(self):
        if len(self.entry_lines) < 2:
            QMessageBox.warning(self, tr("warning_title"), tr("accounting_error_min_lines"))
            return
        try:
            entry_id, entry_number = self.accounting.create_journal_entry(
                self.txt_description.text().strip(), self.entry_lines, self.current_user["id"]
            )
            QMessageBox.information(self, tr("success_title"), tr("accounting_entry_success", number=entry_number))
            self.entry_lines = []
            self.txt_description.clear()
            self._render_lines()
        except ValueError as ve:
            QMessageBox.warning(self, tr("accounting_unbalanced_title"), str(ve))
        except Exception as e:
            QMessageBox.critical(self, tr("warning_title"), tr("accounting_error_submit_entry", error=str(e)))


class GeneralLedgerTab(QWidget):
    def __init__(self, accounting: AccountingModule):
        super().__init__()
        self.accounting = accounting
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        top_row = QHBoxLayout()
        self.cmb_account = QComboBox()
        for a in self.accounting.get_accounts():
            self.cmb_account.addItem(f"{a['code']} - {a['name']}", a["id"])
        self.btn_show = QPushButton()
        self.btn_show.setObjectName("goldButton")
        self.btn_show.clicked.connect(self.show_ledger)
        self.lbl_account = QLabel()
        top_row.addWidget(self.lbl_account)
        top_row.addWidget(self.cmb_account)
        top_row.addWidget(self.btn_show)
        layout.addLayout(top_row)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def retranslate_ui(self):
        self.lbl_account.setText(tr("accounting_account_label"))
        self.btn_show.setText(tr("accounting_show_ledger_btn"))
        self.table.setHorizontalHeaderLabels([
            tr("accounting_col_date"), tr("accounting_col_entry_number"),
            tr("accounting_col_debit"), tr("accounting_col_credit"), tr("accounting_col_balance"),
        ])

    def show_ledger(self):
        account_id = self.cmb_account.currentData()
        ledger = self.accounting.get_general_ledger(account_id)
        self.table.setRowCount(0)
        for row_idx, line in enumerate(ledger):
            self.table.insertRow(row_idx)
            values = [
                line["date"], line["entry_number"], f"{line['debit']:,.0f}",
                f"{line['credit']:,.0f}", f"{line['balance']:,.0f}",
            ]
            for col_idx, val in enumerate(values):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))


class TrialBalanceTab(QWidget):
    def __init__(self, accounting: AccountingModule):
        super().__init__()
        self.accounting = accounting
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.btn_refresh = QPushButton()
        self.btn_refresh.clicked.connect(self.refresh)
        layout.addWidget(self.btn_refresh)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def retranslate_ui(self):
        self.btn_refresh.setText(tr("accounting_refresh_btn"))
        self.table.setHorizontalHeaderLabels([
            tr("accounting_col_code"), tr("accounting_col_account_name"),
            tr("accounting_col_total_debit"), tr("accounting_col_total_credit"),
        ])
        self.refresh()

    def refresh(self):
        rows = self.accounting.get_trial_balance()
        self.table.setRowCount(0)
        for row_idx, r in enumerate(rows):
            self.table.insertRow(row_idx)
            values = [r["code"], r["name"], f"{r['total_debit']:,.0f}", f"{r['total_credit']:,.0f}"]
            for col_idx, val in enumerate(values):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))


class ProfitLossTab(QWidget):
    def __init__(self, accounting: AccountingModule):
        super().__init__()
        self.accounting = accounting
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        date_row = QHBoxLayout()
        self.date_from = QDateEdit(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.btn_show = QPushButton()
        self.btn_show.setObjectName("goldButton")
        self.btn_show.clicked.connect(self.calculate)

        self.lbl_date_from = QLabel()
        self.lbl_date_to = QLabel()
        date_row.addWidget(self.lbl_date_from)
        date_row.addWidget(self.date_from)
        date_row.addWidget(self.lbl_date_to)
        date_row.addWidget(self.date_to)
        date_row.addWidget(self.btn_show)
        layout.addLayout(date_row)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.lbl_result = QLabel("")
        self.lbl_result.setStyleSheet("font-weight: bold; font-size: 15px; color: #1a3a52;")
        layout.addWidget(self.lbl_result)

    def retranslate_ui(self):
        self.lbl_date_from.setText(tr("accounting_date_from_label"))
        self.lbl_date_to.setText(tr("accounting_date_to_label"))
        self.btn_show.setText(tr("accounting_calc_pl_btn"))
        self.table.setHorizontalHeaderLabels([tr("accounting_col_account"), tr("accounting_col_amount")])

    def calculate(self):
        date_from = self.date_from.date().toString("yyyyMMdd")
        date_to = self.date_to.date().toString("yyyyMMdd")
        result = self.accounting.get_profit_and_loss(date_from, date_to)

        self.table.setRowCount(0)
        row_idx = 0
        for acc in result["revenue_accounts"]:
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(tr("accounting_revenue_row", name=acc["name"])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(f"{acc['total_credit'] - acc['total_debit']:,.0f}"))
            row_idx += 1
        for acc in result["expense_accounts"]:
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(tr("accounting_expense_row", name=acc["name"])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(f"{acc['total_debit'] - acc['total_credit']:,.0f}"))
            row_idx += 1

        self.lbl_result.setText(tr(
            "accounting_pl_result",
            revenue=f"{result['total_revenue']:,.0f}",
            expense=f"{result['total_expense']:,.0f}",
            profit=f"{result['net_profit']:,.0f}",
        ))


class BalanceSheetTab(QWidget):
    def __init__(self, accounting: AccountingModule):
        super().__init__()
        self.accounting = accounting
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.btn_show = QPushButton()
        self.btn_show.setObjectName("goldButton")
        self.btn_show.clicked.connect(self.calculate)
        layout.addWidget(self.btn_show)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.lbl_result = QLabel("")
        self.lbl_result.setStyleSheet("font-weight: bold; font-size: 15px; color: #1a3a52;")
        layout.addWidget(self.lbl_result)

    def retranslate_ui(self):
        self.btn_show.setText(tr("accounting_calc_balance_sheet_btn"))
        self.table.setHorizontalHeaderLabels([tr("accounting_col_account"), tr("accounting_col_running_balance")])

    def calculate(self):
        result = self.accounting.get_balance_sheet()
        self.table.setRowCount(0)
        row_idx = 0
        groups = [
            (tr("account_type_asset"), result["assets"]),
            (tr("account_type_liability"), result["liabilities"]),
            (tr("account_type_equity"), result["equity"]),
        ]
        for label, group in groups:
            for acc in group:
                balance = acc["total_debit"] - acc["total_credit"]
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(f"{label} - {acc['name']}"))
                self.table.setItem(row_idx, 1, QTableWidgetItem(f"{balance:,.0f}"))
                row_idx += 1

        self.lbl_result.setText(tr(
            "accounting_bs_result",
            assets=f"{result['total_assets']:,.0f}",
            liabilities=f"{result['total_liabilities']:,.0f}",
            equity=f"{result['total_equity']:,.0f}",
        ))


class ModianTab(QWidget):
    """
    آماده‌سازی اسناد برای سامانه مودیان.
    ⚠️ ارسال واقعی به API سازمان امور مالیاتی در این نسخه پیاده نشده؛
    این تب فقط ساختار داده را آماده و ذخیره می‌کند.
    """

    def __init__(self):
        super().__init__()
        self.modian = ModianModule()
        self._build_ui()
        self._load_settings()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.note = QLabel()
        self.note.setWordWrap(True)
        self.note.setStyleSheet("color: #b23b3b; font-weight: bold;")
        layout.addWidget(self.note)

        settings_form = QFormLayout()

        self.txt_api_url = QLineEdit()
        self.lbl_api_url = QLabel()
        settings_form.addRow(self.lbl_api_url, self.txt_api_url)

        self.txt_certificate_path = QLineEdit()
        self.lbl_certificate_path = QLabel()
        settings_form.addRow(self.lbl_certificate_path, self.txt_certificate_path)

        self.btn_save_settings = QPushButton()
        self.btn_save_settings.setObjectName("saveButton")
        self.btn_save_settings.clicked.connect(self.save_settings)
        settings_form.addRow(self.btn_save_settings)

        layout.addLayout(settings_form)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.txt_preview = QTextEdit()
        self.txt_preview.setReadOnly(True)
        layout.addWidget(self.txt_preview)

    def retranslate_ui(self):
        self.note.setText(tr("modian_warning_note"))
        self.lbl_api_url.setText(tr("modian_api_link_label"))
        self.txt_api_url.setPlaceholderText(tr("modian_api_placeholder"))
        self.lbl_certificate_path.setText(tr("modian_cert_link_label"))
        self.txt_certificate_path.setPlaceholderText(tr("modian_cert_placeholder"))
        self.btn_save_settings.setText(tr("modian_save_settings_btn"))
        self.table.setHorizontalHeaderLabels([
            tr("modian_col_invoice_number"), tr("modian_col_total"), tr("modian_col_status"), "",
        ])
        self.txt_preview.setPlaceholderText(tr("modian_preview_placeholder"))
        self.refresh()

    def refresh(self):
        pending = self.modian.get_pending_invoices()
        self.table.setRowCount(0)
        for row_idx, inv in enumerate(pending):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(inv["invoice_number"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(f"{inv['total_amount']:,.0f}"))
            self.table.setItem(row_idx, 2, QTableWidgetItem(tr("modian_not_prepared")))

            btn_prepare = QPushButton(tr("modian_prepare_btn"))
            btn_prepare.clicked.connect(lambda _, iid=inv["id"]: self.prepare_invoice(iid))
            self.table.setCellWidget(row_idx, 3, btn_prepare)

    def prepare_invoice(self, invoice_id):
        import json
        try:
            payload = self.modian.save_as_ready(invoice_id)
            self.txt_preview.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2))
            QMessageBox.information(self, tr("modian_ready_title"), tr("modian_ready_message"))
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, tr("warning_title"), tr("modian_error_prepare", error=str(e)))

    def _load_settings(self):
        settings = self.modian.get_settings()
        self.txt_api_url.setText(settings["api_url"])
        self.txt_certificate_path.setText(settings["certificate_path"])

    def save_settings(self):
        api_url = self.txt_api_url.text().strip()
        certificate_path = self.txt_certificate_path.text().strip()
        try:
            self.modian.save_settings(api_url, certificate_path)
            QMessageBox.information(self, tr("modian_saved_title"), tr("modian_saved_message"))
        except Exception as e:
            QMessageBox.critical(self, tr("warning_title"), tr("modian_error_save", error=str(e)))


class AccountingPage(QWidget):
    """صفحه اصلی حسابداری؛ فقط برای مدیر فروشگاه و حسابدار در دسترس است."""

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

        if not self.auth.can_manage_products():
            self.lbl_denied = QLabel()
            self.lbl_denied.setWordWrap(True)
            layout.addWidget(self.lbl_denied)
            self.tabs = None
            return

        accounting = AccountingModule()
        self.tabs = QTabWidget()
        self.tab_chart = ChartOfAccountsTab(accounting)
        self.tab_journal = JournalEntryTab(accounting, self.auth.current_user)
        self.tab_ledger = GeneralLedgerTab(accounting)
        self.tab_trial = TrialBalanceTab(accounting)
        self.tab_pl = ProfitLossTab(accounting)
        self.tab_bs = BalanceSheetTab(accounting)
        self.tab_modian = ModianTab()

        self.tabs.addTab(self.tab_chart, "")
        self.tabs.addTab(self.tab_journal, "")
        self.tabs.addTab(self.tab_ledger, "")
        self.tabs.addTab(self.tab_trial, "")
        self.tabs.addTab(self.tab_pl, "")
        self.tabs.addTab(self.tab_bs, "")
        self.tabs.addTab(self.tab_modian, "")
        layout.addWidget(self.tabs)

    def retranslate_ui(self):
        self.title.setText(tr("accounting_page_title"))
        if self.tabs is None:
            self.lbl_denied.setText(tr("accounting_access_denied"))
            return

        self.tabs.setTabText(0, tr("accounting_tab_chart"))
        self.tab_chart.retranslate_ui()
        self.tabs.setTabText(1, tr("accounting_tab_journal"))
        self.tab_journal.retranslate_ui()
        self.tabs.setTabText(2, tr("accounting_tab_ledger"))
        self.tab_ledger.retranslate_ui()
        self.tabs.setTabText(3, tr("accounting_tab_trial_balance"))
        self.tab_trial.retranslate_ui()
        self.tabs.setTabText(4, tr("accounting_tab_profit_loss"))
        self.tab_pl.retranslate_ui()
        self.tabs.setTabText(5, tr("accounting_tab_balance_sheet"))
        self.tab_bs.retranslate_ui()
        self.tabs.setTabText(6, tr("accounting_tab_modian"))
        self.tab_modian.retranslate_ui()
