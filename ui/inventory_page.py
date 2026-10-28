# -*- coding: utf-8 -*-
"""
ui/inventory_page.py
----------------------
مدیریت کالا: افزودن، ویرایش، حذف و مشاهده لیست کالاها با ضریب تبدیل عدد/جعبه
و هشدار نقطه سفارش.

این صفحه از core/i18n.py پشتیبانی می‌کند؛ InventoryPage متد retranslate_ui() دارد.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QDoubleSpinBox, QSpinBox,
    QFormLayout, QDialog, QComboBox, QHeaderView
)
from PyQt6.QtCore import Qt

from modules.inventory import InventoryModule
from core.auth import AuthManager
from core.i18n import tr


class ProductDialog(QDialog):
    """
    دیالوگ افزودن/ویرایش کالا.
    این دیالوگ فقط از داخل InventoryPage باز می‌شود که خودش قبلاً توسط
    AuthManager.can_manage_products() کنترل دسترسی شده (فقط ادمین/حسابدار).
    """

    def __init__(self, parent=None, product=None, inventory_module=None):
        super().__init__(parent)
        self.setWindowTitle(tr("product_dialog_add_title") if product is None else tr("product_dialog_edit_title"))
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.product = product
        self.inventory = inventory_module or InventoryModule()
        self.resize(420, 560)
        self._build_ui()
        if product:
            self._fill_from_product(product)

    def _build_ui(self):
        form = QFormLayout(self)

        self.txt_barcode = QLineEdit()
        self.txt_code = QLineEdit()
        self.txt_name = QLineEdit()
        self.cmb_unit = QComboBox()
        self.cmb_unit.addItem(tr("product_unit_piece"))
        self.cmb_unit.addItem(tr("product_unit_kg"))
        self.cmb_unit.addItem(tr("product_unit_pack"))
        self.cmb_unit.addItem(tr("product_unit_meter"))
        self.spn_units_per_box = QSpinBox()
        self.spn_units_per_box.setRange(1, 100000)
        self.spn_units_per_box.setValue(1)
        self.spn_buy_price = QDoubleSpinBox()
        self.spn_buy_price.setRange(0, 1_000_000_000)
        self.spn_buy_price.setDecimals(0)

        form.addRow(tr("product_barcode_label"), self.txt_barcode)
        form.addRow(tr("product_code_label"), self.txt_code)
        form.addRow(tr("product_name_label"), self.txt_name)
        form.addRow(tr("product_unit_label"), self.cmb_unit)
        form.addRow(tr("product_units_per_box_label"), self.spn_units_per_box)
        form.addRow(tr("product_buy_price_label"), self.spn_buy_price)

        self.cmb_main_group = QComboBox()
        self.cmb_main_group.addItem(tr("product_no_group"), None)
        for g in self.inventory.get_main_groups():
            self.cmb_main_group.addItem(g["name"], g["id"])
        self.cmb_main_group.currentIndexChanged.connect(self._reload_sub_groups)

        self.cmb_sub_group = QComboBox()

        form.addRow(tr("product_main_group_label"), self.cmb_main_group)
        form.addRow(tr("product_sub_group_label"), self.cmb_sub_group)
        self._reload_sub_groups()

        labels = self.inventory.get_price_tier_labels()
        self.price_spinboxes = {}
        for tier in (1, 2, 3, 4):
            spin = QDoubleSpinBox()
            spin.setRange(0, 1_000_000_000)
            spin.setDecimals(0)
            self.price_spinboxes[tier] = spin
            form.addRow(f"{labels.get(tier, tr('product_default_price_tier', n=tier))}:", spin)

        self.spn_min_stock = QDoubleSpinBox()
        self.spn_min_stock.setRange(0, 1_000_000)
        form.addRow(tr("product_min_stock_label"), self.spn_min_stock)

        self.btn_save = QPushButton(tr("save_btn"))
        self.btn_save.setObjectName("saveButton")
        self.btn_save.clicked.connect(self.accept)
        form.addRow(self.btn_save)

    def _reload_sub_groups(self):
        self.cmb_sub_group.clear()
        self.cmb_sub_group.addItem(tr("product_no_subgroup"), None)
        main_id = self.cmb_main_group.currentData()
        if main_id:
            for sg in self.inventory.get_sub_groups(main_id):
                self.cmb_sub_group.addItem(sg["name"], sg["id"])

    def _fill_from_product(self, p):
        self.txt_barcode.setText(p["barcode"] or "")
        self.txt_code.setText(p["code"])
        self.txt_name.setText(p["name"])
        idx = self.cmb_unit.findText(p["unit_type"])
        if idx >= 0:
            self.cmb_unit.setCurrentIndex(idx)
        self.spn_units_per_box.setValue(p["units_per_box"])
        self.spn_buy_price.setValue(p["buy_price"])
        self.price_spinboxes[1].setValue(p["sell_price_1"])
        self.price_spinboxes[2].setValue(p["sell_price_2"])
        self.price_spinboxes[3].setValue(p["sell_price_3"])
        self.price_spinboxes[4].setValue(p["sell_price_4"])
        self.spn_min_stock.setValue(p["min_stock"])

        if p["group_main_id"]:
            idx = self.cmb_main_group.findData(p["group_main_id"])
            if idx >= 0:
                self.cmb_main_group.setCurrentIndex(idx)
        self._reload_sub_groups()
        if p["group_sub_id"]:
            idx = self.cmb_sub_group.findData(p["group_sub_id"])
            if idx >= 0:
                self.cmb_sub_group.setCurrentIndex(idx)

    def get_data(self):
        return {
            "barcode": self.txt_barcode.text().strip() or None,
            "code": self.txt_code.text().strip(),
            "name": self.txt_name.text().strip(),
            "unit_type": self.cmb_unit.currentText(),
            "units_per_box": self.spn_units_per_box.value(),
            "buy_price": self.spn_buy_price.value(),
            "sell_price_1": self.price_spinboxes[1].value(),
            "sell_price_2": self.price_spinboxes[2].value(),
            "sell_price_3": self.price_spinboxes[3].value(),
            "sell_price_4": self.price_spinboxes[4].value(),
            "group_main_id": self.cmb_main_group.currentData(),
            "group_sub_id": self.cmb_sub_group.currentData(),
            "min_stock": self.spn_min_stock.value(),
        }


class InventoryPage(QWidget):
    """
    مدیریت کالا و انبار.
    طبق قانون دسترسی، این صفحه (تعریف/ویرایش کالا، تعیین قیمت‌ها و گروه‌بندی)
    فقط برای «مدیر فروشگاه» (admin) و «حسابدار» (accountant) در دسترس است.
    صندوق‌دار به این صفحه دسترسی ندارد و فقط در فاکتور فروش از قیمت‌های
    از پیش تعیین‌شده استفاده می‌کند.
    """

    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self.inventory = InventoryModule()
        self._build_ui()
        self.retranslate_ui()
        if self.auth.can_manage_products():
            self.refresh_table()

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
            return

        toolbar = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.textChanged.connect(self.refresh_table)

        self.btn_add = QPushButton()
        self.btn_add.setObjectName("goldButton")
        self.btn_add.clicked.connect(self.add_product)

        self.btn_edit = QPushButton()
        self.btn_edit.clicked.connect(self.edit_product)

        self.btn_delete = QPushButton()
        self.btn_delete.setObjectName("dangerButton")
        self.btn_delete.clicked.connect(self.delete_product)

        self.btn_add_group = QPushButton()
        self.btn_add_group.clicked.connect(self.add_group)

        self.btn_edit_labels = QPushButton()
        self.btn_edit_labels.clicked.connect(self.edit_price_labels)

        toolbar.addWidget(self.btn_delete)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_add_group)
        toolbar.addWidget(self.btn_edit_labels)
        toolbar.addStretch()
        toolbar.addWidget(self.txt_search)

        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount() - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(self.table.columnCount() - 1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def retranslate_ui(self):
        self.title.setText(tr("inventory_page_title"))
        if not self.auth.can_manage_products():
            self.lbl_denied.setText(tr("inventory_access_denied"))
            return

        self.txt_search.setPlaceholderText(tr("inventory_search_placeholder"))
        self.btn_add.setText(tr("inventory_add_product_btn"))
        self.btn_edit.setText(tr("edit_btn"))
        self.btn_delete.setText(tr("delete_btn"))
        self.btn_add_group.setText(tr("inventory_add_group_btn"))
        self.btn_edit_labels.setText(tr("inventory_edit_labels_btn"))

        price_labels = self.inventory.get_price_tier_labels()
        self.table.setHorizontalHeaderLabels([
            tr("inventory_col_id"), tr("inventory_col_barcode"), tr("inventory_col_code"),
            tr("inventory_col_name"), tr("inventory_col_stock"),
            price_labels.get(1, tr("product_default_price_tier", n=1)),
            price_labels.get(2, tr("product_default_price_tier", n=2)),
            price_labels.get(3, tr("product_default_price_tier", n=3)),
            price_labels.get(4, tr("product_default_price_tier", n=4)),
        ])

    def refresh_table(self):
        keyword = self.txt_search.text().strip()
        products = self.inventory.search_products(keyword) if keyword else self.inventory.get_all_products()

        self.table.setRowCount(0)
        for row_idx, p in enumerate(products):
            self.table.insertRow(row_idx)
            values = [
                p["id"], p["barcode"] or "-", p["code"], p["name"], p["stock_qty"],
                p["sell_price_1"], p["sell_price_2"], p["sell_price_3"], p["sell_price_4"],
            ]
            for col_idx, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col_idx == 4 and p["stock_qty"] <= p["min_stock"]:
                    item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row_idx, col_idx, item)

    def _get_selected_product_id(self):
        selected = self.table.currentRow()
        if selected < 0:
            return None
        return int(self.table.item(selected, 0).text())

    def add_product(self):
        dialog = ProductDialog(self, inventory_module=self.inventory)
        if dialog.exec():
            data = dialog.get_data()
            if not data["code"] or not data["name"]:
                QMessageBox.warning(self, tr("warning_title"), tr("inventory_error_code_name_required"))
                return
            try:
                self.inventory.add_product(
                    data["barcode"], data["code"], data["name"], data["unit_type"],
                    data["units_per_box"], data["buy_price"],
                    data["sell_price_1"], data["sell_price_2"],
                    data["sell_price_3"], data["sell_price_4"],
                    data["min_stock"], data["group_main_id"], data["group_sub_id"],
                )
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, tr("warning_title"), tr("inventory_error_save", error=str(e)))

    def edit_product(self):
        product_id = self._get_selected_product_id()
        if product_id is None:
            QMessageBox.information(self, tr("info_title"), tr("inventory_select_first"))
            return
        product = self.inventory.db.fetch_one("SELECT * FROM products WHERE id = ?;", (product_id,))
        dialog = ProductDialog(self, product=product, inventory_module=self.inventory)
        if dialog.exec():
            data = dialog.get_data()
            self.inventory.update_product(product_id, **data)
            self.refresh_table()

    def delete_product(self):
        product_id = self._get_selected_product_id()
        if product_id is None:
            QMessageBox.information(self, tr("info_title"), tr("inventory_select_first"))
            return
        confirm = QMessageBox.question(
            self, tr("inventory_confirm_delete_title"), tr("inventory_confirm_delete_message")
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.inventory.delete_product(product_id)
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, tr("warning_title"), tr("inventory_error_delete", error=str(e)))

    def add_group(self):
        main_groups = self.inventory.get_main_groups()
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("inventory_add_group_dialog_title"))
        dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        form = QFormLayout(dialog)

        cmb_parent = QComboBox()
        cmb_parent.addItem(tr("inventory_group_type_new_main"), None)
        for g in main_groups:
            cmb_parent.addItem(tr("inventory_group_type_sub_for", name=g["name"]), g["id"])

        txt_name = QLineEdit()
        form.addRow(tr("inventory_group_type_label"), cmb_parent)
        form.addRow(tr("inventory_group_name_label"), txt_name)

        btn_save = QPushButton(tr("save_btn"))
        btn_save.setObjectName("saveButton")
        btn_save.clicked.connect(dialog.accept)
        form.addRow(btn_save)

        if dialog.exec():
            name = txt_name.text().strip()
            if not name:
                QMessageBox.warning(self, tr("warning_title"), tr("inventory_error_group_name_required"))
                return
            try:
                self.inventory.add_category(name, cmb_parent.currentData())
                QMessageBox.information(self, tr("success_title"), tr("inventory_group_added_message"))
            except Exception as e:
                QMessageBox.critical(self, tr("warning_title"), tr("inventory_error_add_group", error=str(e)))

    def edit_price_labels(self):
        labels = self.inventory.get_price_tier_labels()
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("inventory_edit_labels_dialog_title"))
        dialog.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        form = QFormLayout(dialog)

        txt_boxes = {}
        for tier in (1, 2, 3, 4):
            txt = QLineEdit(labels.get(tier, tr("product_default_price_tier", n=tier)))
            txt_boxes[tier] = txt
            form.addRow(tr("inventory_price_label_row", n=tier), txt)

        btn_save = QPushButton(tr("save_btn"))
        btn_save.setObjectName("saveButton")
        btn_save.clicked.connect(dialog.accept)
        form.addRow(btn_save)

        if dialog.exec():
            for tier, txt in txt_boxes.items():
                new_label = txt.text().strip()
                if new_label:
                    self.inventory.update_price_tier_label(tier, new_label)
            QMessageBox.information(self, tr("success_title"), tr("inventory_labels_updated_message"))
            self.retranslate_ui()
            self.refresh_table()
