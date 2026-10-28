# -*- coding: utf-8 -*-
"""
ui/checks_page.py
--------------------
مدیریت چک‌های دریافتی (از مشتری) و پرداختی (به تامین‌کننده).
وصول/برگشت چک به‌صورت خودکار در خزانه و حسابداری ثبت می‌شود.
این صفحه از core/i18n.py پشتیبانی می‌کند؛ ChecksPage متد retranslate_ui() دارد.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QDoubleSpinBox,
    QDateEdit, QDialog, QFormLayout
)
from PyQt6.QtCore import Qt, QDate

from core.auth import AuthManager
from modules.checks import CheckModule
from core.i18n import tr


class ChecksPage(QWidget):
    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self.checks = CheckModule()
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        self.title = QLabel()
        self.title.setObjectName("pageTitle")
        layout.addWidget(self.title)

        form_row = QHBoxLayout()
        self.txt_check_number = QLineEdit()
        self.txt_bank_name = QLineEdit()
        self.spn_amount = QDoubleSpinBox()
        self.spn_amount.setRange(0, 1_000_000_000)
        self.spn_amount.setDecimals(0)
        self.date_due = QDateEdit(QDate.currentDate())
        self.date_due.setCalendarPopup(True)
        self.cmb_direction = QComboBox()
        self.cmb_direction.addItem("", "received")
        self.cmb_direction.addItem("", "issued")

        self.btn_register = QPushButton()
        self.btn_register.setObjectName("goldButton")
        self.btn_register.clicked.connect(self.register_check)

        form_row.addWidget(self.txt_check_number)
        form_row.addWidget(self.txt_bank_name)
        form_row.addWidget(self.spn_amount)
        form_row.addWidget(self.date_due)
        form_row.addWidget(self.cmb_direction)
        form_row.addWidget(self.btn_register)
        layout.addLayout(form_row)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        action_row = QHBoxLayout()
        self.btn_collect = QPushButton()
        self.btn_collect.setObjectName("goldButton")
        self.btn_collect.clicked.connect(self.collect_selected)

        self.btn_bounce = QPushButton()
        self.btn_bounce.setObjectName("dangerButton")
        self.btn_bounce.clicked.connect(self.bounce_selected)

        self.btn_edit = QPushButton()
        self.btn_edit.clicked.connect(self.edit_selected)

        self.btn_delete = QPushButton()
        self.btn_delete.setObjectName("dangerButton")
        self.btn_delete.clicked.connect(self.delete_selected)

        action_row.addWidget(self.btn_collect)
        action_row.addWidget(self.btn_bounce)
        action_row.addWidget(self.btn_edit)
        action_row.addWidget(self.btn_delete)
        action_row.addStretch()
        layout.addLayout(action_row)

    def retranslate_ui(self):
        self.title.setText(tr("checks_page_title"))
        self.txt_check_number.setPlaceholderText(tr("checks_number_placeholder"))
        self.txt_bank_name.setPlaceholderText(tr("checks_bank_placeholder"))
        self.cmb_direction.setItemText(0, tr("checks_direction_received"))
        self.cmb_direction.setItemText(1, tr("checks_direction_issued"))
        self.btn_register.setText(tr("checks_register_btn"))
        self.table.setHorizontalHeaderLabels([
            tr("checks_col_id"), tr("checks_col_number"), tr("checks_col_bank"),
            tr("checks_col_amount"), tr("checks_col_due_date"), tr("checks_col_type"), tr("checks_col_status"),
        ])
        self.btn_collect.setText(tr("checks_collect_btn"))
        self.btn_bounce.setText(tr("checks_bounce_btn"))
        self.btn_edit.setText(tr("checks_edit_btn"))
        self.btn_delete.setText(tr("checks_delete_btn"))
        self.refresh()

    def refresh(self):
        status_labels = {
            "pending": tr("checks_status_pending"), "collected": tr("checks_status_collected"),
            "bounced": tr("checks_status_bounced"), "transferred": tr("checks_status_transferred"),
        }
        rows = self.checks.get_checks()
        self.table.setRowCount(0)
        for row_idx, c in enumerate(rows):
            self.table.insertRow(row_idx)
            direction_label = tr("checks_row_received") if c["direction"] == "received" else tr("checks_row_issued")
            values = [
                str(c["id"]), c["check_number"], c["bank_name"] or "-",
                f"{c['amount']:,.0f}", c["due_date"], direction_label,
                status_labels.get(c["status"], c["status"]),
            ]
            for col_idx, val in enumerate(values):
                item = QTableWidgetItem(val)
                if c["status"] == "bounced":
                    item.setForeground(Qt.GlobalColor.red)
                elif c["status"] == "collected":
                    item.setForeground(Qt.GlobalColor.darkGreen)
                self.table.setItem(row_idx, col_idx, item)

    def _get_selected_check_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def register_check(self):
        check_number = self.txt_check_number.text().strip()
        amount = self.spn_amount.value()
        if not check_number or amount <= 0:
            QMessageBox.warning(self, tr("warning_title"), tr("checks_error_required"))
            return

        box_id = self.auth.current_user["box_id"]
        if box_id is None:
            QMessageBox.warning(self, tr("warning_title"), tr("checks_error_no_box"))
            return

        try:
            self.checks.register_check(
                check_number=check_number,
                bank_name=self.txt_bank_name.text().strip(),
                amount=amount,
                due_date=self.date_due.date().toString("yyyyMMdd"),
                direction=self.cmb_direction.currentData(),
                party_id=None,
                box_id=box_id,
                user_id=self.auth.current_user["id"],
            )
            self.txt_check_number.clear()
            self.txt_bank_name.clear()
            self.spn_amount.setValue(0)
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, tr("warning_title"), tr("checks_error_register", error=str(e)))

    def collect_selected(self):
        check_id = self._get_selected_check_id()
        if check_id is None:
            QMessageBox.information(self, tr("info_title"), tr("checks_select_first"))
            return
        try:
            self.checks.mark_collected(check_id, self.auth.current_user["id"])
            QMessageBox.information(self, tr("success_title"), tr("checks_collect_success"))
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, tr("warning_title"), str(e))

    def bounce_selected(self):
        check_id = self._get_selected_check_id()
        if check_id is None:
            QMessageBox.information(self, tr("info_title"), tr("checks_select_first"))
            return
        confirm = QMessageBox.question(self, tr("checks_confirm_title"), tr("checks_confirm_bounce"))
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.checks.mark_bounced(check_id)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, tr("warning_title"), str(e))

    def edit_selected(self):
        """
        ویرایش چک انتخاب‌شده. فقط چک‌های «در انتظار وصول» قابل ویرایش هستند
        (بررسی نهایی در ماژول CheckModule.update_check انجام می‌شود).
        """
        check_id = self._get_selected_check_id()
        if check_id is None:
            QMessageBox.information(self, tr("info_title"), tr("checks_select_first"))
            return

        check = self.checks.db.fetch_one("SELECT * FROM checks WHERE id = ?;", (check_id,))
        if check is None:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("checks_edit_dialog_title"))
        dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        form = QFormLayout(dialog)

        txt_number = QLineEdit(check["check_number"])
        txt_bank = QLineEdit(check["bank_name"] or "")
        spn_amount = QDoubleSpinBox()
        spn_amount.setRange(0, 1_000_000_000)
        spn_amount.setDecimals(0)
        spn_amount.setValue(check["amount"])
        date_due = QDateEdit()
        date_due.setCalendarPopup(True)
        date_due.setDate(QDate.fromString(check["due_date"], "yyyyMMdd"))
        txt_description = QLineEdit(check["description"] or "")

        form.addRow(tr("checks_number_label"), txt_number)
        form.addRow(tr("checks_bank_label"), txt_bank)
        form.addRow(tr("checks_amount_label"), spn_amount)
        form.addRow(tr("checks_due_date_label"), date_due)
        form.addRow(tr("checks_description_label"), txt_description)

        btn_save = QPushButton(tr("save_btn"))
        btn_save.setObjectName("saveButton")
        btn_save.clicked.connect(dialog.accept)
        form.addRow(btn_save)

        if dialog.exec():
            try:
                self.checks.update_check(
                    check_id, txt_number.text().strip(), txt_bank.text().strip(),
                    spn_amount.value(), date_due.date().toString("yyyyMMdd"),
                    txt_description.text().strip(),
                )
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, tr("warning_title"), str(e))

    def delete_selected(self):
        check_id = self._get_selected_check_id()
        if check_id is None:
            QMessageBox.information(self, tr("info_title"), tr("checks_select_first"))
            return
        confirm = QMessageBox.question(self, tr("invoices_confirm_delete_title"), tr("checks_confirm_delete"))
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.checks.delete_check(check_id)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, tr("warning_title"), str(e))
