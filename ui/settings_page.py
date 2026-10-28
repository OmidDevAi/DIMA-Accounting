# -*- coding: utf-8 -*-
"""
ui/settings_page.py
----------------------
مدیریت کاربران (فقط برای ادمین): تعریف کاربر جدید و تخصیص به یک صندوق مشخص،
مدیریت صندوق‌ها، تنظیمات بارکدخوان و تنظیمات سرویس پیامک.
این صفحه از core/i18n.py پشتیبانی می‌کند؛ SettingsPage.retranslate_ui() همه‌ی
تب‌ها را هم به‌روزرسانی می‌کند.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QFormLayout,
    QTabWidget, QSpinBox, QDialog
)
from PyQt6.QtCore import Qt

from core.auth import AuthManager
from core.db_manager import DBManager
from modules.scanner_settings import ScannerSettingsModule
from core.barcode_scanner import PYSERIAL_AVAILABLE
from modules.sms import SMSModule
from core.i18n import tr


class UsersTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DBManager.instance()
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.txt_username = QLineEdit()
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_fullname = QLineEdit()
        self.cmb_role = QComboBox()
        self.cmb_role.addItem("", "cashier")
        self.cmb_role.addItem("", "accountant")
        self.cmb_role.addItem("", "admin")
        self.cmb_box = QComboBox()
        self._load_boxes()

        self.lbl_username = QLabel()
        self.lbl_password = QLabel()
        self.lbl_fullname = QLabel()
        self.lbl_role = QLabel()
        self.lbl_box = QLabel()
        form.addRow(self.lbl_username, self.txt_username)
        form.addRow(self.lbl_password, self.txt_password)
        form.addRow(self.lbl_fullname, self.txt_fullname)
        form.addRow(self.lbl_role, self.cmb_role)
        form.addRow(self.lbl_box, self.cmb_box)

        self.btn_create = QPushButton()
        self.btn_create.setObjectName("goldButton")
        self.btn_create.clicked.connect(self.create_user)
        form.addRow(self.btn_create)

        layout.addLayout(form)

        action_row = QHBoxLayout()
        self.btn_edit = QPushButton()
        self.btn_edit.clicked.connect(self.edit_user)
        self.btn_password = QPushButton()
        self.btn_password.clicked.connect(self.change_password)
        self.btn_toggle_active = QPushButton()
        self.btn_toggle_active.setObjectName("dangerButton")
        self.btn_toggle_active.clicked.connect(self.toggle_active)
        action_row.addWidget(self.btn_edit)
        action_row.addWidget(self.btn_password)
        action_row.addWidget(self.btn_toggle_active)
        action_row.addStretch()
        layout.addLayout(action_row)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def retranslate_ui(self):
        self.lbl_username.setText(tr("settings_username_label"))
        self.lbl_password.setText(tr("settings_password_label"))
        self.lbl_fullname.setText(tr("settings_fullname_label"))
        self.lbl_role.setText(tr("settings_role_label"))
        self.cmb_role.setItemText(0, tr("settings_role_cashier"))
        self.cmb_role.setItemText(1, tr("settings_role_accountant"))
        self.cmb_role.setItemText(2, tr("settings_role_admin"))
        self.lbl_box.setText(tr("settings_box_label"))
        self.btn_create.setText(tr("settings_create_user_btn"))
        self.btn_edit.setText(tr("settings_edit_user_btn"))
        self.btn_password.setText(tr("settings_change_password_btn"))
        self.btn_toggle_active.setText(tr("settings_toggle_active_btn"))
        self.table.setHorizontalHeaderLabels([
            tr("settings_col_id"), tr("settings_col_username"), tr("settings_col_fullname"),
            tr("settings_col_role"), tr("settings_col_box"), tr("settings_col_status"),
        ])
        self.refresh()

    def _load_boxes(self):
        self.cmb_box.clear()
        boxes = self.db.fetch_all("SELECT * FROM cash_boxes WHERE is_active = 1;")
        for b in boxes:
            self.cmb_box.addItem(b["name"], b["id"])

    def refresh(self):
        rows = self.db.fetch_all(
            """SELECT u.id, u.username, u.full_name, u.role, u.is_active, cb.name AS box_name
               FROM users u LEFT JOIN cash_boxes cb ON u.box_id = cb.id
               ORDER BY u.id;"""
        )
        self.table.setRowCount(0)
        role_labels = {
            "admin": tr("settings_role_admin"), "accountant": tr("settings_role_accountant"),
            "cashier": tr("settings_role_cashier"),
        }
        for row_idx, r in enumerate(rows):
            self.table.insertRow(row_idx)
            role_label = role_labels.get(r["role"], r["role"])
            status_label = tr("settings_status_active") if r["is_active"] else tr("settings_status_inactive")
            values = [str(r["id"]), r["username"], r["full_name"], role_label, r["box_name"] or "-", status_label]
            for col_idx, val in enumerate(values):
                item = QTableWidgetItem(val)
                if col_idx == 5 and not r["is_active"]:
                    item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row_idx, col_idx, item)

    def create_user(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()
        full_name = self.txt_fullname.text().strip()

        if not username or not password or not full_name:
            QMessageBox.warning(self, tr("warning_title"), tr("settings_error_all_fields"))
            return

        try:
            AuthManager.create_user(
                username, password, full_name,
                self.cmb_role.currentData(), self.cmb_box.currentData()
            )
            QMessageBox.information(self, tr("success_title"), tr("settings_user_created"))
            self.txt_username.clear()
            self.txt_password.clear()
            self.txt_fullname.clear()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, tr("warning_title"), tr("settings_error_create_user", error=str(e)))

    def _selected_user_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def edit_user(self):
        user_id = self._selected_user_id()
        if user_id is None:
            QMessageBox.information(self, tr("info_title"), tr("settings_select_user_first"))
            return

        user = self.db.fetch_one("SELECT * FROM users WHERE id = ?;", (user_id,))
        if user is None:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("settings_edit_user_dialog_title"))
        dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        form = QFormLayout(dialog)

        txt_fullname = QLineEdit(user["full_name"])
        cmb_role = QComboBox()
        cmb_role.addItem(tr("settings_role_cashier"), "cashier")
        cmb_role.addItem(tr("settings_role_accountant"), "accountant")
        cmb_role.addItem(tr("settings_role_admin"), "admin")
        idx = cmb_role.findData(user["role"])
        if idx >= 0:
            cmb_role.setCurrentIndex(idx)

        cmb_box = QComboBox()
        boxes = self.db.fetch_all("SELECT * FROM cash_boxes WHERE is_active = 1;")
        for b in boxes:
            cmb_box.addItem(b["name"], b["id"])
        box_idx = cmb_box.findData(user["box_id"])
        if box_idx >= 0:
            cmb_box.setCurrentIndex(box_idx)

        form.addRow(tr("settings_fullname_label"), txt_fullname)
        form.addRow(tr("settings_role_label"), cmb_role)
        form.addRow(tr("settings_box_label"), cmb_box)

        btn_save = QPushButton(tr("save_btn"))
        btn_save.setObjectName("saveButton")
        btn_save.clicked.connect(dialog.accept)
        form.addRow(btn_save)

        if dialog.exec():
            AuthManager.update_user(
                user_id, txt_fullname.text().strip(), cmb_role.currentData(), cmb_box.currentData()
            )
            self.refresh()

    def change_password(self):
        user_id = self._selected_user_id()
        if user_id is None:
            QMessageBox.information(self, tr("info_title"), tr("settings_select_user_first"))
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(tr("settings_change_password_dialog_title"))
        dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        form = QFormLayout(dialog)

        txt_new_password = QLineEdit()
        txt_new_password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow(tr("settings_new_password_label"), txt_new_password)

        btn_save = QPushButton(tr("save_btn"))
        btn_save.setObjectName("saveButton")
        btn_save.clicked.connect(dialog.accept)
        form.addRow(btn_save)

        if dialog.exec():
            new_password = txt_new_password.text()
            if not new_password:
                QMessageBox.warning(self, tr("warning_title"), tr("settings_error_empty_password"))
                return
            AuthManager.set_user_password(user_id, new_password)
            QMessageBox.information(self, tr("success_title"), tr("settings_password_changed"))

    def toggle_active(self):
        user_id = self._selected_user_id()
        if user_id is None:
            QMessageBox.information(self, tr("info_title"), tr("settings_select_user_first"))
            return

        user = self.db.fetch_one("SELECT * FROM users WHERE id = ?;", (user_id,))
        if user is None:
            return

        new_state = not bool(user["is_active"])
        action_label = tr("settings_action_activate") if new_state else tr("settings_action_deactivate")
        confirm = QMessageBox.question(
            self, tr("checks_confirm_title"),
            tr("settings_confirm_toggle", action=action_label, name=user["full_name"])
        )
        if confirm == QMessageBox.StandardButton.Yes:
            AuthManager.set_user_active(user_id, new_state)
            self.refresh()


class BoxesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DBManager.instance()
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form_row = QHBoxLayout()
        self.txt_box_name = QLineEdit()
        self.btn_add = QPushButton()
        self.btn_add.setObjectName("goldButton")
        self.btn_add.clicked.connect(self.add_box)
        form_row.addWidget(self.txt_box_name)
        form_row.addWidget(self.btn_add)
        layout.addLayout(form_row)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def retranslate_ui(self):
        self.txt_box_name.setPlaceholderText(tr("settings_new_box_placeholder"))
        self.btn_add.setText(tr("settings_add_box_btn"))
        self.table.setHorizontalHeaderLabels([
            tr("settings_col_id"), tr("settings_col_box_name"), tr("settings_col_status"),
        ])
        self.refresh()

    def refresh(self):
        boxes = self.db.fetch_all("SELECT * FROM cash_boxes ORDER BY id;")
        self.table.setRowCount(0)
        for row_idx, b in enumerate(boxes):
            self.table.insertRow(row_idx)
            status = tr("settings_status_active") if b["is_active"] else tr("settings_status_inactive")
            for col_idx, val in enumerate([str(b["id"]), b["name"], status]):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))

    def add_box(self):
        name = self.txt_box_name.text().strip()
        if not name:
            return
        try:
            self.db.execute("INSERT INTO cash_boxes (name, is_active) VALUES (?, 1);", (name,))
            self.txt_box_name.clear()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, tr("warning_title"), tr("settings_error_add_box", error=str(e)))


class ScannerSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.scanner_settings = ScannerSettingsModule()
        self._build_ui()
        self._load()
        self.retranslate_ui()

    def _build_ui(self):
        form = QFormLayout(self)

        self.note = QLabel()
        self.note.setWordWrap(True)
        form.addRow(self.note)

        self.warn = None
        if not PYSERIAL_AVAILABLE:
            self.warn = QLabel()
            self.warn.setWordWrap(True)
            self.warn.setStyleSheet("color: #b23b3b; font-weight: bold;")
            form.addRow(self.warn)

        self.cmb_mode = QComboBox()
        self.cmb_mode.addItem("", "usb")
        self.cmb_mode.addItem("", "serial")
        self.lbl_connection_type = QLabel()
        form.addRow(self.lbl_connection_type, self.cmb_mode)

        self.txt_port = QLineEdit()
        self.lbl_serial_port = QLabel()
        form.addRow(self.lbl_serial_port, self.txt_port)

        self.spn_baud = QSpinBox()
        self.spn_baud.setRange(1200, 115200)
        self.spn_baud.setValue(9600)
        self.lbl_baud_rate = QLabel()
        form.addRow(self.lbl_baud_rate, self.spn_baud)

        self.btn_save = QPushButton()
        self.btn_save.setObjectName("saveButton")
        self.btn_save.clicked.connect(self.save)
        form.addRow(self.btn_save)

        self.hint = QLabel()
        self.hint.setStyleSheet("color: #888888; font-size: 11px;")
        form.addRow(self.hint)

    def retranslate_ui(self):
        self.note.setText(tr("settings_scanner_note"))
        if self.warn is not None:
            self.warn.setText(tr("settings_pyserial_warning"))
        self.cmb_mode.setItemText(0, tr("settings_scanner_mode_usb"))
        self.cmb_mode.setItemText(1, tr("settings_scanner_mode_serial"))
        self.lbl_connection_type.setText(tr("settings_connection_type_label"))
        self.lbl_serial_port.setText(tr("settings_serial_port_label"))
        self.txt_port.setPlaceholderText(tr("settings_serial_port_placeholder"))
        self.lbl_baud_rate.setText(tr("settings_baud_rate_label"))
        self.btn_save.setText(tr("settings_save_settings_btn"))
        self.hint.setText(tr("settings_restart_hint"))

    def _load(self):
        settings = self.scanner_settings.get_settings()
        idx = self.cmb_mode.findData(settings["mode"])
        if idx >= 0:
            self.cmb_mode.setCurrentIndex(idx)
        self.txt_port.setText(settings["port"])
        self.spn_baud.setValue(settings["baud_rate"])

    def save(self):
        self.scanner_settings.save_settings(
            self.cmb_mode.currentData(), self.txt_port.text().strip(), self.spn_baud.value()
        )
        QMessageBox.information(self, tr("modian_saved_title"), tr("settings_scanner_saved_message"))


class SMSSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.sms = SMSModule()
        self._build_ui()
        self._load()
        self.retranslate_ui()

    def _build_ui(self):
        form = QFormLayout(self)

        self.note = QLabel()
        self.note.setWordWrap(True)
        self.note.setStyleSheet("color: #b23b3b; font-weight: bold;")
        form.addRow(self.note)

        self.cmb_provider = QComboBox()
        self.cmb_provider.addItem("", "kavenegar")
        self.cmb_provider.addItem("", "melipayamak")
        self.cmb_provider.addItem("", "generic")
        self.cmb_provider.currentIndexChanged.connect(self._update_field_visibility)
        self.lbl_provider = QLabel()
        form.addRow(self.lbl_provider, self.cmb_provider)

        self.txt_api_key = QLineEdit()
        self.lbl_api_key = QLabel()
        form.addRow(self.lbl_api_key, self.txt_api_key)

        self.txt_api_url = QLineEdit()
        self.lbl_api_url = QLabel()
        form.addRow(self.lbl_api_url, self.txt_api_url)

        self.txt_sender = QLineEdit()
        self.lbl_sender = QLabel()
        form.addRow(self.lbl_sender, self.txt_sender)

        self.cmb_http_method = QComboBox()
        self.cmb_http_method.addItem("POST", "POST")
        self.cmb_http_method.addItem("GET", "GET")
        self.lbl_http_method = QLabel()
        form.addRow(self.lbl_http_method, self.cmb_http_method)

        self.txt_payload_template = QLineEdit()
        self.lbl_payload_template = QLabel()
        form.addRow(self.lbl_payload_template, self.txt_payload_template)

        self.hint = QLabel()
        self.hint.setWordWrap(True)
        self.hint.setStyleSheet("color: #888888; font-size: 11px;")
        form.addRow(self.hint)

        self.btn_save = QPushButton()
        self.btn_save.setObjectName("saveButton")
        self.btn_save.clicked.connect(self.save)
        form.addRow(self.btn_save)

    def retranslate_ui(self):
        self.note.setText(tr("settings_sms_note"))
        self.cmb_provider.setItemText(0, tr("settings_provider_kavenegar"))
        self.cmb_provider.setItemText(1, tr("settings_provider_melipayamak"))
        self.cmb_provider.setItemText(2, tr("settings_provider_generic"))
        self.lbl_provider.setText(tr("settings_provider_label"))
        self.lbl_api_key.setText(tr("settings_api_key_label"))
        self.txt_api_key.setPlaceholderText(tr("settings_api_key_placeholder"))
        self.lbl_api_url.setText(tr("settings_api_url_label"))
        self.txt_api_url.setPlaceholderText(tr("settings_api_url_placeholder"))
        self.lbl_sender.setText(tr("settings_sender_label"))
        self.txt_sender.setPlaceholderText(tr("settings_sender_placeholder"))
        self.lbl_http_method.setText(tr("settings_http_method_label"))
        self.lbl_payload_template.setText(tr("settings_payload_template_label"))
        self.txt_payload_template.setPlaceholderText(
            '{"to": "{phone}", "text": "{message}", "from": "{sender}", "key": "{api_key}"}'
        )
        self.hint.setText(tr("settings_payload_hint"))
        self.btn_save.setText(tr("settings_save_settings_btn"))

    def _update_field_visibility(self):
        is_generic = self.cmb_provider.currentData() == "generic"
        self.cmb_http_method.setEnabled(is_generic)
        self.txt_payload_template.setEnabled(is_generic)

    def _load(self):
        settings = self.sms.get_settings()
        idx = self.cmb_provider.findData(settings["provider"])
        if idx >= 0:
            self.cmb_provider.setCurrentIndex(idx)
        self.txt_api_key.setText(settings["api_key"])
        self.txt_api_url.setText(settings["api_url"])
        self.txt_sender.setText(settings["sender_number"])
        method_idx = self.cmb_http_method.findData(settings["http_method"])
        if method_idx >= 0:
            self.cmb_http_method.setCurrentIndex(method_idx)
        self.txt_payload_template.setText(settings["payload_template"])
        self._update_field_visibility()

    def save(self):
        self.sms.save_settings(
            provider=self.cmb_provider.currentData(),
            api_url=self.txt_api_url.text().strip(),
            api_key=self.txt_api_key.text().strip(),
            sender_number=self.txt_sender.text().strip(),
            http_method=self.cmb_http_method.currentData(),
            payload_template=self.txt_payload_template.text().strip(),
        )
        QMessageBox.information(self, tr("modian_saved_title"), tr("settings_sms_saved_message"))


class SettingsPage(QWidget):
    """صفحه تنظیمات فقط برای کاربران ادمین قابل دسترسی است."""

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

        if not self.auth.is_admin():
            self.lbl_denied = QLabel()
            layout.addWidget(self.lbl_denied)
            self.tabs = None
            return

        self.tabs = QTabWidget()
        self.tab_users = UsersTab()
        self.tab_boxes = BoxesTab()
        self.tab_scanner = ScannerSettingsTab()
        self.tab_sms = SMSSettingsTab()
        self.tabs.addTab(self.tab_users, "")
        self.tabs.addTab(self.tab_boxes, "")
        self.tabs.addTab(self.tab_scanner, "")
        self.tabs.addTab(self.tab_sms, "")
        layout.addWidget(self.tabs)

    def retranslate_ui(self):
        self.title.setText(tr("settings_page_title"))
        if self.tabs is None:
            self.lbl_denied.setText(tr("settings_access_denied"))
            return

        self.tabs.setTabText(0, tr("settings_tab_users"))
        self.tab_users.retranslate_ui()
        self.tabs.setTabText(1, tr("settings_tab_boxes"))
        self.tab_boxes.retranslate_ui()
        self.tabs.setTabText(2, tr("settings_tab_scanner"))
        self.tab_scanner.retranslate_ui()
        self.tabs.setTabText(3, tr("settings_tab_sms"))
        self.tab_sms.retranslate_ui()
