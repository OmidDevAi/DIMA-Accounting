# -*- coding: utf-8 -*-
"""
ui/purchase_page.py
----------------------
فاکتور خرید پیشرفته.
به‌جای جدول قابل‌ویرایش مستقیم، هر کالا از طریق دکمه‌ی «+ افزودن کالا» و یک
فرم پاپ‌آپ مجزا (PurchaseItemDialog) وارد می‌شود؛ جدول اصلی این صفحه فقط
خلاصه‌ی کالاهای اضافه‌شده را نمایش می‌دهد.

این صفحه از core/i18n.py پشتیبانی می‌کند؛ PurchasePage متد retranslate_ui() دارد.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QDoubleSpinBox,
    QDateEdit, QHeaderView, QCheckBox, QDialog, QFormLayout
)
from PyQt6.QtCore import Qt, QDate

from core.auth import AuthManager
from modules.purchase import PurchaseModule
from modules.inventory import InventoryModule
from ui.invoice_receipt_dialog import InvoiceReceiptDialog
from core.i18n import tr


SUMMARY_COLUMN_KEYS = [
    "purchase_col_barcode", "purchase_col_code", "purchase_col_name",
    "purchase_col_qty_num", "purchase_col_qty_box", "purchase_col_gift",
    "purchase_col_buy_price", "purchase_col_discount", "purchase_col_tax",
    "purchase_col_line_total", None,
]


class PurchaseItemDialog(QDialog):
    """
    فرم پاپ‌آپ افزودن یک کالا به فاکتور خرید.
    بارکد یا کد کالا را وارد/جستجو می‌کنید، بقیه‌ی اطلاعات کالا (نام)
    خودکار پر می‌شود و تعداد/هدیه/تخفیف/مالیات/تاریخ تولید-انقضا را وارد می‌کنید.
    """

    def __init__(self, parent, inventory: InventoryModule):
        super().__init__(parent)
        self.inventory = inventory
        self.resolved_product = None
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(420, 520)
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        self.form = QFormLayout(self)

        search_row = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.returnPressed.connect(self.resolve_product)
        self.btn_search = QPushButton()
        self.btn_search.clicked.connect(self.resolve_product)
        search_row.addWidget(self.txt_search)
        search_row.addWidget(self.btn_search)
        self.lbl_search_row = QLabel()
        self.form.addRow(self.lbl_search_row, search_row)

        self.lbl_product_name_row = QLabel()
        self.lbl_product_name = QLabel()
        self.lbl_product_name.setStyleSheet("font-weight: bold; color: #1a3a52;")
        self.form.addRow(self.lbl_product_name_row, self.lbl_product_name)

        self.spn_qty_num = QDoubleSpinBox()
        self.spn_qty_num.setRange(0, 1_000_000)
        self.spn_qty_box = QDoubleSpinBox()
        self.spn_qty_box.setRange(0, 1_000_000)
        self.spn_gift_qty = QDoubleSpinBox()
        self.spn_gift_qty.setRange(0, 1_000_000)

        self.lbl_qty_num_row = QLabel()
        self.form.addRow(self.lbl_qty_num_row, self.spn_qty_num)
        self.lbl_qty_box_row = QLabel()
        self.form.addRow(self.lbl_qty_box_row, self.spn_qty_box)
        self.lbl_gift_row = QLabel()
        self.form.addRow(self.lbl_gift_row, self.spn_gift_qty)

        self.spn_price = QDoubleSpinBox()
        self.spn_price.setRange(0, 1_000_000_000)
        self.spn_price.setDecimals(0)
        self.lbl_price_row = QLabel()
        self.form.addRow(self.lbl_price_row, self.spn_price)

        self.spn_discount = QDoubleSpinBox()
        self.spn_discount.setRange(0, 1_000_000_000)
        self.spn_discount.setDecimals(0)
        self.cmb_discount_type = QComboBox()
        self.cmb_discount_type.addItem("", "rial")
        self.cmb_discount_type.addItem("", "percent")
        discount_row = QHBoxLayout()
        discount_row.addWidget(self.spn_discount)
        discount_row.addWidget(self.cmb_discount_type)
        self.lbl_discount_row = QLabel()
        self.form.addRow(self.lbl_discount_row, discount_row)

        self.chk_has_tax = QCheckBox()
        self.spn_tax_percent = QDoubleSpinBox()
        self.spn_tax_percent.setRange(0, 100)
        self.spn_tax_percent.setValue(9)
        tax_row = QHBoxLayout()
        tax_row.addWidget(self.chk_has_tax)
        self.lbl_percent = QLabel()
        tax_row.addWidget(self.lbl_percent)
        tax_row.addWidget(self.spn_tax_percent)
        self.lbl_tax_row = QLabel()
        self.form.addRow(self.lbl_tax_row, tax_row)

        self.date_prod = QDateEdit(QDate.currentDate())
        self.date_prod.setCalendarPopup(True)
        self.date_exp = QDateEdit(QDate.currentDate())
        self.date_exp.setCalendarPopup(True)
        self.lbl_prod_date_row = QLabel()
        self.form.addRow(self.lbl_prod_date_row, self.date_prod)
        self.lbl_exp_date_row = QLabel()
        self.form.addRow(self.lbl_exp_date_row, self.date_exp)

        self.btn_save = QPushButton()
        self.btn_save.setObjectName("saveButton")
        self.btn_save.clicked.connect(self.try_accept)
        self.form.addRow(self.btn_save)

    def retranslate_ui(self):
        self.setWindowTitle(tr("purchase_item_dialog_title"))
        self.lbl_search_row.setText(tr("purchase_item_search_label"))
        self.txt_search.setPlaceholderText(tr("purchase_item_search_placeholder"))
        self.btn_search.setText(tr("search_btn"))
        self.lbl_product_name_row.setText(tr("purchase_item_name_label"))
        if self.resolved_product is None:
            self.lbl_product_name.setText(tr("purchase_item_no_selection"))
        self.lbl_qty_num_row.setText(tr("purchase_item_qty_num_label"))
        self.lbl_qty_box_row.setText(tr("purchase_item_qty_box_label"))
        self.lbl_gift_row.setText(tr("purchase_item_gift_label"))
        self.lbl_price_row.setText(tr("purchase_item_price_label"))
        self.lbl_discount_row.setText(tr("purchase_item_discount_label"))
        self.cmb_discount_type.setItemText(0, tr("discount_type_rial"))
        self.cmb_discount_type.setItemText(1, tr("discount_type_percent"))
        self.chk_has_tax.setText(tr("purchase_item_has_tax_checkbox"))
        self.lbl_percent.setText(tr("purchase_item_percent_label"))
        self.lbl_tax_row.setText(tr("purchase_item_tax_label"))
        self.lbl_prod_date_row.setText(tr("purchase_item_prod_date_label"))
        self.lbl_exp_date_row.setText(tr("purchase_item_exp_date_label"))
        self.btn_save.setText(tr("purchase_item_add_btn"))

    def resolve_product(self):
        text = self.txt_search.text().strip()
        if not text:
            return
        product = self.inventory.find_by_barcode(text)
        if product is None:
            product = self.inventory.db.fetch_one("SELECT * FROM products WHERE code = ?;", (text,))
        if product is None:
            QMessageBox.warning(self, tr("purchase_item_not_found_title"), tr("purchase_item_not_found_message"))
            self.resolved_product = None
            self.lbl_product_name.setText(tr("purchase_item_no_selection"))
            return

        self.resolved_product = product
        self.lbl_product_name.setText(f"{product['name']} ({product['code']})")
        self.spn_price.setValue(0)

    def try_accept(self):
        if self.resolved_product is None:
            QMessageBox.warning(self, tr("warning_title"), tr("purchase_item_error_no_product"))
            return
        if self.spn_qty_num.value() == 0 and self.spn_qty_box.value() == 0:
            QMessageBox.warning(self, tr("warning_title"), tr("purchase_item_error_no_qty"))
            return
        if self.spn_price.value() <= 0:
            QMessageBox.warning(self, tr("warning_title"), tr("purchase_item_error_no_price"))
            return
        self.accept()

    def get_item_data(self):
        return {
            "product_id": self.resolved_product["id"],
            "barcode": self.resolved_product["barcode"] or "",
            "code": self.resolved_product["code"],
            "name": self.resolved_product["name"],
            "units_per_box": self.resolved_product["units_per_box"],
            "qty_num": self.spn_qty_num.value(),
            "qty_box": self.spn_qty_box.value(),
            "gift_qty": self.spn_gift_qty.value(),
            "price": self.spn_price.value(),
            "discount_amount": self.spn_discount.value(),
            "discount_type": self.cmb_discount_type.currentData(),
            "has_tax": self.chk_has_tax.isChecked(),
            "tax_percent": self.spn_tax_percent.value() if self.chk_has_tax.isChecked() else 0,
            "prod_date": self.date_prod.date().toString("yyyy-MM-dd"),
            "exp_date": self.date_exp.date().toString("yyyy-MM-dd"),
        }


class PurchasePage(QWidget):
    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self.purchase = PurchaseModule()
        self.inventory = InventoryModule()
        self.items_data = []
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        self.title = QLabel()
        self.title.setObjectName("pageTitle")
        layout.addWidget(self.title)

        supplier_row = QHBoxLayout()
        self.lbl_supplier = QLabel()
        self.cmb_supplier = QComboBox()
        self._load_suppliers()
        self.lbl_payment = QLabel()
        self.cmb_payment = QComboBox()
        self.cmb_payment.addItem("", "cash")
        self.cmb_payment.addItem("", "credit")

        supplier_row.addWidget(self.lbl_supplier)
        supplier_row.addWidget(self.cmb_supplier)
        supplier_row.addWidget(self.lbl_payment)
        supplier_row.addWidget(self.cmb_payment)
        supplier_row.addStretch()

        self.btn_add_item = QPushButton()
        self.btn_add_item.setObjectName("goldButton")
        self.btn_add_item.clicked.connect(self.open_add_item_dialog)
        supplier_row.addWidget(self.btn_add_item)

        layout.addLayout(supplier_row)

        self.table = QTableWidget()
        self.table.setColumnCount(len(SUMMARY_COLUMN_KEYS))
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.table.horizontalHeader()
        for col in range(len(SUMMARY_COLUMN_KEYS) - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(len(SUMMARY_COLUMN_KEYS) - 1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        totals_row = QHBoxLayout()
        self.spn_invoice_discount = QDoubleSpinBox()
        self.spn_invoice_discount.setRange(0, 1_000_000_000)
        self.spn_invoice_discount.setDecimals(0)
        self.spn_invoice_discount.valueChanged.connect(self.recalc_total)
        self.cmb_invoice_discount_type = QComboBox()
        self.cmb_invoice_discount_type.addItem("", "rial")
        self.cmb_invoice_discount_type.addItem("", "percent")
        self.cmb_invoice_discount_type.currentIndexChanged.connect(self.recalc_total)

        self.spn_duty = QDoubleSpinBox()
        self.spn_duty.setRange(0, 1_000_000_000)
        self.spn_duty.setDecimals(0)
        self.spn_duty.valueChanged.connect(self.recalc_total)

        self.lbl_invoice_discount = QLabel()
        self.lbl_duty = QLabel()
        totals_row.addWidget(self.lbl_invoice_discount)
        totals_row.addWidget(self.spn_invoice_discount)
        totals_row.addWidget(self.cmb_invoice_discount_type)
        totals_row.addWidget(self.lbl_duty)
        totals_row.addWidget(self.spn_duty)
        totals_row.addStretch()
        layout.addLayout(totals_row)

        bottom_row = QHBoxLayout()
        self.lbl_total = QLabel()
        self.lbl_total.setStyleSheet("font-weight: bold; font-size: 16px; color: #1a3a52;")

        self.btn_submit = QPushButton()
        self.btn_submit.setObjectName("goldButton")
        self.btn_submit.clicked.connect(self.submit_invoice)

        bottom_row.addStretch()
        bottom_row.addWidget(self.lbl_total)
        bottom_row.addWidget(self.btn_submit)
        layout.addLayout(bottom_row)

    def retranslate_ui(self):
        self.title.setText(tr("purchase_page_title"))
        self.lbl_supplier.setText(tr("purchase_supplier_label"))
        self.cmb_supplier.setItemText(0, tr("purchase_no_supplier"))
        self.lbl_payment.setText(tr("purchase_payment_label"))
        self.cmb_payment.setItemText(0, tr("payment_cash"))
        self.cmb_payment.setItemText(1, tr("payment_credit"))
        self.btn_add_item.setText(tr("purchase_add_item_btn"))
        self.table.setHorizontalHeaderLabels(
            [tr(key) if key else "" for key in SUMMARY_COLUMN_KEYS]
        )
        self.lbl_invoice_discount.setText(tr("purchase_invoice_discount_label"))
        self.cmb_invoice_discount_type.setItemText(0, tr("discount_type_rial"))
        self.cmb_invoice_discount_type.setItemText(1, tr("discount_type_percent"))
        self.lbl_duty.setText(tr("purchase_duty_label"))
        self.btn_submit.setText(tr("purchase_submit_btn"))
        self._render_table()

    def _load_suppliers(self):
        self.cmb_supplier.clear()
        self.cmb_supplier.addItem(tr("purchase_no_supplier"), None)
        suppliers = self.inventory.db.fetch_all(
            "SELECT * FROM parties WHERE type = 'supplier' ORDER BY name;"
        )
        for s in suppliers:
            self.cmb_supplier.addItem(s["name"], s["id"])

    def open_add_item_dialog(self):
        dialog = PurchaseItemDialog(self, self.inventory)
        if dialog.exec():
            self.items_data.append(dialog.get_item_data())
            self._render_table()

    def _calc_line_total(self, item):
        units_per_box = item["units_per_box"]
        base_qty = item["qty_num"] + (item["qty_box"] * units_per_box)
        line_subtotal = base_qty * item["price"]
        discount = line_subtotal * (item["discount_amount"] / 100.0) \
            if item["discount_type"] == "percent" else item["discount_amount"]
        after_discount = line_subtotal - discount
        tax_amount = after_discount * (item["tax_percent"] / 100.0) if item["has_tax"] else 0
        return after_discount + tax_amount

    def _render_table(self):
        self.table.setRowCount(0)
        for row_idx, item in enumerate(self.items_data):
            self.table.insertRow(row_idx)
            line_total = self._calc_line_total(item)
            discount_type_label = tr("discount_type_percent") if item["discount_type"] == "percent" else tr("discount_type_rial")
            discount_label = f"{item['discount_amount']:,.0f} {discount_type_label}"
            tax_label = f"{item['tax_percent']:.0f}%" if item["has_tax"] else "—"

            values = [
                item["barcode"], item["code"], item["name"],
                str(item["qty_num"]), str(item["qty_box"]), str(item["gift_qty"]),
                f"{item['price']:,.0f}", discount_label, tax_label, f"{line_total:,.0f}",
            ]
            for col_idx, val in enumerate(values):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))

            btn_remove = QPushButton(tr("remove_btn"))
            btn_remove.setObjectName("dangerButton")
            btn_remove.clicked.connect(lambda _, r=row_idx: self.remove_item(r))
            self.table.setCellWidget(row_idx, len(SUMMARY_COLUMN_KEYS) - 1, btn_remove)

        self.recalc_total()

    def remove_item(self, row_idx):
        if 0 <= row_idx < len(self.items_data):
            del self.items_data[row_idx]
            self._render_table()

    def recalc_total(self):
        subtotal = sum(self._calc_line_total(item) for item in self.items_data)
        discount_value = subtotal * (self.spn_invoice_discount.value() / 100.0) \
            if self.cmb_invoice_discount_type.currentData() == "percent" \
            else self.spn_invoice_discount.value()
        total = subtotal - discount_value + self.spn_duty.value()
        self.lbl_total.setText(tr("purchase_total_label", amount=f"{total:,.0f}"))

    def submit_invoice(self):
        if not self.items_data:
            QMessageBox.information(self, tr("info_title"), tr("purchase_empty_items"))
            return

        box_id = self.auth.current_user["box_id"]
        if box_id is None:
            QMessageBox.warning(self, tr("warning_title"), tr("purchase_no_active_box"))
            return

        try:
            invoice_id, invoice_number, total = self.purchase.create_purchase_invoice(
                party_id=self.cmb_supplier.currentData(),
                user_id=self.auth.current_user["id"],
                box_id=box_id,
                payment_type=self.cmb_payment.currentData(),
                items=self.items_data,
                invoice_discount=self.spn_invoice_discount.value(),
                invoice_discount_type=self.cmb_invoice_discount_type.currentData(),
                duty_amount=self.spn_duty.value(),
            )
            QMessageBox.information(
                self, tr("sales_success_title"),
                tr("purchase_success_message", number=invoice_number, amount=f"{total:,.0f}")
            )
            receipt = InvoiceReceiptDialog(self, tr("purchase_invoice_label"), invoice_number, self.items_data, total)
            receipt.exec()

            self.items_data = []
            self.spn_invoice_discount.setValue(0)
            self.spn_duty.setValue(0)
            self._render_table()
        except Exception as e:
            QMessageBox.critical(self, tr("warning_title"), tr("purchase_error_submit", error=str(e)))
