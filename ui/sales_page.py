# -*- coding: utf-8 -*-
"""
ui/sales_page.py
------------------
فاکتور فروش سریع (خرده و عمده) با پشتیبانی از **چند فاکتور باز هم‌زمان**
برای یک صندوق (مثلاً وقتی یک فاکتور نیمه‌تمام مانده و صندوق‌دار باید هم‌زمان
فاکتور مشتری دیگری را هم شروع/ثبت کند).

معماری:
    - SaleCartWidget: منطق و UI «یک فاکتور» (همان چیزی که قبلاً کل SalesPage بود)
    - SalesPage: کانتینر تب‌دار که چند نمونه از SaleCartWidget را هم‌زمان نگه
      می‌دارد؛ هر تب یک فاکتور کاملاً مستقل و جداگانه است (سبد، مشتری، تخفیف و...)

Hotkey ها (F2/F6/F11/Delete/F9) در سطح SalesPage (کانتینر) ثبت می‌شوند و به
تبِ فعلیِ انتخاب‌شده هدایت می‌شوند، تا در تمام تب‌ها یکسان کار کنند.

این صفحه از core/i18n.py پشتیبانی می‌کند؛ هر دو کلاس متد retranslate_ui() دارند.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QDoubleSpinBox,
    QCheckBox, QTabWidget, QHeaderView, QApplication, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut

from core.auth import AuthManager
from modules.sales import SalesModule
from modules.inventory import InventoryModule
from modules.customers import CustomerModule
from ui.invoice_receipt_dialog import InvoiceReceiptDialog
from modules.scanner_settings import ScannerSettingsModule
from core.barcode_scanner import SerialBarcodeReader, PYSERIAL_AVAILABLE
from core.i18n import tr


class SaleCartWidget(QWidget):
    """
    منطق و رابط کاربری «یک فاکتور فروش». چند نمونه از این ویجت می‌توانند
    هم‌زمان در تب‌های مختلف صفحه‌ی فروش باز باشند، هرکدام کاملاً مستقل.
    """

    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self.sales = SalesModule()
        self.inventory = InventoryModule()
        self.customers = CustomerModule()
        self.cart_items = []  # لیست موقت اقلام همین فاکتور (مستقل از تب‌های دیگر)
        # برچسب‌های ۴ سطح قیمت که توسط مدیر/حسابدار در صفحه انبار تعیین شده‌اند
        # (این برچسب‌ها داده‌ی کاربر هستند، نه بخشی از ترجمه‌ی زبان رابط کاربری)
        self.price_tier_labels = self.inventory.get_price_tier_labels()
        self._build_ui()
        self.retranslate_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # ------------- ورودی بارکد و نام مشتری -------------
        scan_row = QHBoxLayout()
        self.lbl_scan = QLabel()
        self.txt_barcode = QLineEdit()
        self.txt_barcode.returnPressed.connect(self.handle_barcode_scan)

        self.lbl_customer_phone = QLabel()
        self.txt_customer_phone = QLineEdit()

        self.txt_customer_name = QLineEdit()

        self.chk_wholesale = QCheckBox()

        scan_row.addWidget(self.lbl_scan)
        scan_row.addWidget(self.txt_barcode)
        scan_row.addWidget(self.lbl_customer_phone)
        scan_row.addWidget(self.txt_customer_phone)
        scan_row.addWidget(self.txt_customer_name)
        scan_row.addWidget(self.chk_wholesale)
        layout.addLayout(scan_row)

        # ------------- جدول سبد فروش -------------
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount() - 1):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 185)
        header.setSectionResizeMode(self.table.columnCount() - 1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(34)
        layout.addWidget(self.table)

        # ------------- تخفیف کل فاکتور -------------
        discount_row = QHBoxLayout()
        self.lbl_invoice_discount = QLabel()
        self.spn_invoice_discount = QDoubleSpinBox()
        self.spn_invoice_discount.setRange(0, 1_000_000_000)
        self.spn_invoice_discount.setDecimals(0)
        self.spn_invoice_discount.valueChanged.connect(self._render_cart)
        self.cmb_invoice_discount_type = QComboBox()
        self.cmb_invoice_discount_type.addItem("", "rial")
        self.cmb_invoice_discount_type.addItem("", "percent")
        self.cmb_invoice_discount_type.currentIndexChanged.connect(self._render_cart)

        discount_row.addWidget(self.lbl_invoice_discount)
        discount_row.addWidget(self.spn_invoice_discount)
        discount_row.addWidget(self.cmb_invoice_discount_type)
        discount_row.addStretch()
        layout.addLayout(discount_row)

        # ------------- نوع پرداخت و ثبت -------------
        bottom_row = QHBoxLayout()
        self.lbl_payment = QLabel()
        self.cmb_payment = QComboBox()
        self.cmb_payment.addItem("", "cash")
        self.cmb_payment.addItem("", "credit")
        self.cmb_payment.addItem("", "card")

        self.lbl_total = QLabel()
        self.lbl_total.setStyleSheet("font-weight: bold; font-size: 16px; color: #1a3a52;")

        self.btn_submit = QPushButton()
        self.btn_submit.setObjectName("goldButton")
        self.btn_submit.clicked.connect(self.submit_invoice)

        bottom_row.addWidget(self.lbl_payment)
        bottom_row.addWidget(self.cmb_payment)
        bottom_row.addStretch()
        bottom_row.addWidget(self.lbl_total)
        bottom_row.addWidget(self.btn_submit)

        layout.addLayout(bottom_row)

    def retranslate_ui(self):
        """به‌روزرسانی تمام متن‌های ثابت این ویجت طبق زبان جاری."""
        self.lbl_scan.setText(tr("sales_scan_barcode_label"))
        self.txt_barcode.setPlaceholderText(tr("sales_scan_barcode_placeholder"))
        self.lbl_customer_phone.setText(tr("sales_customer_phone_label"))
        self.txt_customer_phone.setPlaceholderText(tr("sales_customer_phone_placeholder"))
        self.txt_customer_name.setPlaceholderText(tr("sales_customer_name_placeholder"))
        self.chk_wholesale.setText(tr("sales_wholesale_checkbox"))

        self.table.setHorizontalHeaderLabels([
            tr("sales_col_product_id"), tr("sales_col_product_name"), tr("sales_col_qty"),
            tr("sales_col_price_tier"), tr("sales_col_unit_price"), tr("sales_col_line_total"), "",
        ])

        self.lbl_invoice_discount.setText(tr("sales_invoice_discount_label"))
        self.cmb_invoice_discount_type.setItemText(0, tr("discount_type_rial"))
        self.cmb_invoice_discount_type.setItemText(1, tr("discount_type_percent"))

        self.lbl_payment.setText(tr("sales_payment_type_label"))
        self.cmb_payment.setItemText(0, tr("payment_cash"))
        self.cmb_payment.setItemText(1, tr("payment_credit"))
        self.cmb_payment.setItemText(2, tr("payment_card"))

        self.btn_submit.setText(tr("sales_submit_btn"))
        self._render_cart()  # جمع کل و متن دکمه‌های حذف هر ردیف هم به‌روز شوند

    # ---------- عملیاتی که از هات‌کی‌های سطح صفحه (SalesPage) فراخوانی می‌شوند ----------
    def toggle_wholesale(self):
        self.chk_wholesale.setChecked(not self.chk_wholesale.isChecked())

    def submit_as_cash(self):
        idx = self.cmb_payment.findData("cash")
        if idx >= 0:
            self.cmb_payment.setCurrentIndex(idx)
        self.submit_invoice()

    def submit_as_card(self):
        idx = self.cmb_payment.findData("card")
        if idx >= 0:
            self.cmb_payment.setCurrentIndex(idx)
        self.submit_invoice()

    # ------------------------------------------------------------
    def handle_barcode_scan(self):
        barcode = self.txt_barcode.text().strip()
        self.txt_barcode.clear()
        if not barcode:
            return

        product = self.sales.find_product_by_barcode(barcode)
        if product is None:
            QMessageBox.warning(self, tr("sales_not_found_title"), tr("sales_not_found_message", barcode=barcode))
            return

        for existing in self.cart_items:
            if existing["product_id"] == product["id"]:
                existing["qty_num"] += 1
                self._render_cart()
                return

        default_tier = 1
        self.cart_items.append({
            "product_id": product["id"],
            "name": product["name"],
            "qty_num": 1,
            "qty_box": 0,
            "prices": {
                1: product["sell_price_1"],
                2: product["sell_price_2"],
                3: product["sell_price_3"],
                4: product["sell_price_4"],
            },
            "price_tier": default_tier,
            "price": product[f"sell_price_{default_tier}"],
            "units_per_box": product["units_per_box"],
        })
        self._render_cart()

    def _render_cart(self):
        self.table.setRowCount(0)
        subtotal = 0
        for row_idx, item in enumerate(self.cart_items):
            self.table.insertRow(row_idx)
            line_total = item["qty_num"] * item["price"]
            subtotal += line_total

            values = [str(item["product_id"]), item["name"], str(item["qty_num"])]
            for col_idx, val in enumerate(values):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(val))

            cmb_tier = QComboBox()
            for tier in (1, 2, 3, 4):
                label = self.price_tier_labels.get(tier, f"Price {tier}")
                price_value = item["prices"].get(tier, 0)
                cmb_tier.addItem(f"{label} ({price_value:,.0f})", tier)
            current_idx = cmb_tier.findData(item["price_tier"])
            if current_idx >= 0:
                cmb_tier.setCurrentIndex(current_idx)
            cmb_tier.currentIndexChanged.connect(
                lambda _, r=row_idx, c=cmb_tier: self._change_price_tier(r, c.currentData())
            )
            self.table.setCellWidget(row_idx, 3, cmb_tier)

            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{item['price']:,.0f}"))
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"{line_total:,.0f}"))

            btn_remove = QPushButton(tr("remove_btn"))
            btn_remove.setObjectName("dangerButton")
            btn_remove.clicked.connect(lambda _, r=row_idx: self._remove_item(r))
            self.table.setCellWidget(row_idx, 6, btn_remove)

        discount_value = subtotal * (self.spn_invoice_discount.value() / 100.0) \
            if self.cmb_invoice_discount_type.currentData() == "percent" \
            else self.spn_invoice_discount.value()
        total = subtotal - discount_value
        self.lbl_total.setText(tr("sales_total_label", amount=f"{total:,.0f}"))

    def _change_price_tier(self, row_idx, tier):
        if tier is None or not (0 <= row_idx < len(self.cart_items)):
            return
        item = self.cart_items[row_idx]
        item["price_tier"] = tier
        item["price"] = item["prices"].get(tier, 0)
        self._render_cart()

    def _remove_item(self, row_idx):
        if 0 <= row_idx < len(self.cart_items):
            del self.cart_items[row_idx]
            self._render_cart()

    def remove_selected_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self._remove_item(row)

    def resolve_customer(self):
        phone = self.txt_customer_phone.text().strip()
        if not phone:
            return None, True

        name = self.txt_customer_name.text().strip()
        customer_id = self.customers.get_or_create_customer(phone, name or None)

        if customer_id is None:
            entered_name, ok = QInputDialog.getText(
                self, tr("sales_new_customer_title"), tr("sales_new_customer_prompt", phone=phone)
            )
            if not ok or not entered_name.strip():
                return None, False
            customer_id = self.customers.get_or_create_customer(phone, entered_name.strip())

        return customer_id, True

    def submit_invoice(self):
        if not self.cart_items:
            QMessageBox.information(self, tr("info_title"), tr("sales_empty_cart"))
            return

        box_id = self.auth.current_user["box_id"]
        if box_id is None:
            QMessageBox.warning(self, tr("warning_title"), tr("sales_no_active_box"))
            return

        customer_id, ok = self.resolve_customer()
        if not ok:
            return

        payment_type = self.cmb_payment.currentData()

        try:
            invoice_id, invoice_number, total = self.sales.create_sale_invoice(
                party_id=customer_id,
                user_id=self.auth.current_user["id"],
                box_id=box_id,
                payment_type=payment_type,
                items=self.cart_items,
                invoice_discount=self.spn_invoice_discount.value(),
                invoice_discount_type=self.cmb_invoice_discount_type.currentData(),
                is_wholesale=self.chk_wholesale.isChecked(),
            )
            QMessageBox.information(
                self, tr("sales_success_title"),
                tr("sales_success_message", number=invoice_number, amount=f"{total:,.0f}")
            )
            receipt = InvoiceReceiptDialog(
                self, tr("sales_invoice_sale_label"), invoice_number, self.cart_items, total
            )
            receipt.exec()

            self.cart_items = []
            self.spn_invoice_discount.setValue(0)
            self.txt_customer_name.clear()
            self.txt_customer_phone.clear()
            self._render_cart()
        except ValueError as ve:
            QMessageBox.warning(self, tr("sales_stock_error_title"), str(ve))
        except Exception as e:
            QMessageBox.critical(self, tr("warning_title"), f"{e}")


class SalesPage(QWidget):
    """
    کانتینر چند-فاکتوره‌ی فروش سریع.
    """

    def __init__(self):
        super().__init__()
        self._invoice_counter = 0
        self._build_ui()
        self._setup_hotkeys()
        self.add_new_invoice_tab()
        self.scanner_thread = None
        self._setup_serial_scanner()
        self.retranslate_ui()

    def _setup_serial_scanner(self):
        settings = ScannerSettingsModule().get_settings()
        if settings["mode"] != "serial" or not settings["port"]:
            return
        if not PYSERIAL_AVAILABLE:
            QMessageBox.warning(
                self, "Serial Barcode Scanner",
                "Serial scanner mode is enabled but the pyserial library is not installed.\n"
                "Run 'pip install pyserial'."
            )
            return

        self.scanner_thread = SerialBarcodeReader(settings["port"], settings["baud_rate"])
        self.scanner_thread.barcode_scanned.connect(self._on_serial_barcode)
        self.scanner_thread.error_occurred.connect(self._on_scanner_error)
        self.scanner_thread.start()

        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.scanner_thread.stop)

    def _on_serial_barcode(self, barcode: str):
        cart = self._current_cart()
        if cart:
            cart.txt_barcode.setText(barcode)
            cart.handle_barcode_scan()

    def _on_scanner_error(self, message: str):
        QMessageBox.warning(self, "Serial Barcode Scanner", message)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title_row = QHBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("pageTitle")
        self.btn_new_tab = QPushButton()
        self.btn_new_tab.setObjectName("goldButton")
        self.btn_new_tab.clicked.connect(self.add_new_invoice_tab)

        title_row.addWidget(self.title)
        title_row.addStretch()
        title_row.addWidget(self.btn_new_tab)
        layout.addLayout(title_row)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tabs)

    def retranslate_ui(self):
        self.title.setText(tr("sales_page_title"))
        self.btn_new_tab.setText(tr("sales_new_invoice_btn"))
        for i in range(self.tabs.count()):
            self.tabs.setTabText(i, tr("sales_tab_name", n=i + 1))
            cart_widget = self.tabs.widget(i)
            if hasattr(cart_widget, "retranslate_ui"):
                cart_widget.retranslate_ui()

    def add_new_invoice_tab(self):
        self._invoice_counter += 1
        cart_widget = SaleCartWidget()
        index = self.tabs.addTab(cart_widget, tr("sales_tab_name", n=self._invoice_counter))
        self.tabs.setCurrentIndex(index)

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        if widget is not None and widget.cart_items:
            confirm = QMessageBox.question(
                self, tr("info_title"),
                "This invoice is not yet submitted and still has items in the cart. "
                "Are you sure you want to close it without submitting?"
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return

        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            self.add_new_invoice_tab()

    def _setup_hotkeys(self):
        QShortcut(QKeySequence("F2"), self, activated=self._forward_cash)
        QShortcut(QKeySequence("F6"), self, activated=self._forward_card)
        QShortcut(QKeySequence("F11"), self, activated=self._forward_wholesale)
        QShortcut(QKeySequence("Delete"), self, activated=self._forward_delete)
        QShortcut(QKeySequence("F9"), self, activated=self._forward_delete)

    def _current_cart(self):
        return self.tabs.currentWidget()

    def _forward_cash(self):
        cart = self._current_cart()
        if cart:
            cart.submit_as_cash()

    def _forward_card(self):
        cart = self._current_cart()
        if cart:
            cart.submit_as_card()

    def _forward_wholesale(self):
        cart = self._current_cart()
        if cart:
            cart.toggle_wholesale()

    def _forward_delete(self):
        cart = self._current_cart()
        if cart:
            cart.remove_selected_row()
