# -*- coding: utf-8 -*-
"""
ui/main_window.py
--------------------
پنجره اصلی (داشبورد) برنامه پس از ورود موفق.
شامل منوی کناری (سرمه‌ای/طلایی) برای ناوبری بین ماژول‌ها و QStackedWidget
برای نمایش صفحات مختلف.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QLabel, QFrame, QStatusBar, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize

from core.i18n import tr, set_language, get_language, get_layout_direction, SUPPORTED_LANGUAGES
from modules.app_settings import AppSettingsModule

# qtawesome آیکون‌های فونت‌محور (مثل فونت‌آست) را در PyQt فراهم می‌کند.
# اگر نصب نشده باشد، برنامه بدون آیکون (فقط با متن) اجرا می‌شود تا هیچ‌وقت کرش نکند.
try:
    import qtawesome as qta
    QTAWESOME_AVAILABLE = True
except ImportError:
    QTAWESOME_AVAILABLE = False

from core.auth import AuthManager
from ui.dashboard_page import DashboardPage
from ui.sales_page import SalesPage
from ui.purchase_page import PurchasePage
from ui.inventory_page import InventoryPage
from ui.treasury_page import TreasuryPage
from ui.checks_page import ChecksPage
from ui.accounting_page import AccountingPage
from ui.customers_page import CustomersPage
from ui.invoices_page import InvoicesPage
from ui.about_page import AboutPage
from ui.settings_page import SettingsPage


class SidebarButton(QFrame):
    """
    آیتم منوی کناری (متن + آیکون، راست‌چین واقعی).
    به‌جای QPushButton از QFrame استفاده شده، چون QPushButton رندر ویجت‌های
    داخل لایوت دستی خودش را به‌درستی نمی‌کشد و متن نامرئی می‌شود؛ کلیک هم
    به‌صورت دستی با mousePressEvent پیاده شده است.
    """
    clicked = pyqtSignal()

    def __init__(self, label_text, icon_name=None, danger=False, parent=None):
        super().__init__(parent)
        self._checked = False
        self.danger = danger
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        self.text_label = QLabel(label_text)

        # نکته مهم: چون پنجره RTL است، Qt ترتیب اضافه‌شدن آیتم‌ها را خودکار آینه می‌کند.
        # برای اینکه در نتیجه‌ی نهایی، آیکون در لبه‌ی راست و متن کنار آن (و فضای خالی
        # سمت چپ) قرار بگیرد، باید ترتیب افزودن را برعکسِ چیدمان دیداری موردنظر بدهیم:
        # اول آیکون، بعد متن، در آخر stretch.
        if QTAWESOME_AVAILABLE and icon_name:
            icon_label = QLabel()
            icon_label.setPixmap(qta.icon(icon_name, color="white").pixmap(16, 16))
            icon_label.setStyleSheet("background: transparent;")
            layout.addWidget(icon_label)

        layout.addWidget(self.text_label)
        layout.addStretch()

        self._apply_style()

    def _apply_style(self):
        if self.danger:
            bg, text_color, weight = "#b23b3b", "#ffffff", "normal"
        else:
            bg = "#d4af37" if self._checked else "transparent"
            text_color = "#1a3a52" if self._checked else "#ffffff"
            weight = "bold" if self._checked else "normal"
        self.setStyleSheet(f"background-color: {bg};")
        self.text_label.setStyleSheet(f"color: {text_color}; background: transparent; font-weight: {weight};")

    def setChecked(self, checked: bool):
        self._checked = checked
        self._apply_style()

    def isChecked(self):
        return self._checked

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    # سیگنال خروج از حساب؛ main.py آن را می‌شنود و پنجره ورود را دوباره نمایش می‌دهد
    logged_out = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.auth = AuthManager.instance()
        self.setWindowTitle(tr("app_title"))
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(1200, 720)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ------------- منوی کناری -------------
        self.side_menu = QFrame()
        self.side_menu.setObjectName("sideMenu")
        self.side_menu.setFixedWidth(220)
        menu_layout = QVBoxLayout(self.side_menu)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(2)

        # ------------- دکمه همبرگری برای جمع‌کردن/بازکردن سایدبار (ریسپانسیو) -------------
        self.sidebar_expanded = True
        btn_hamburger = QPushButton()
        btn_hamburger.setMinimumHeight(44)  # تضمین ارتفاع قابل‌مشاهده حتی بدون آیکون
        if QTAWESOME_AVAILABLE:
            btn_hamburger.setIcon(qta.icon("fa5s.bars", color="white"))
            btn_hamburger.setIconSize(QSize(18, 18))
            btn_hamburger.setStyleSheet("background: transparent; border: none; padding: 14px;")
        else:
            # اگر qtawesome نصب نباشد، بدون این متن جایگزین دکمه کاملاً نامرئی می‌شد
            # (نه آیکون داشت، نه متن)؛ این تضمین می‌کند همیشه چیزی دیده شود.
            btn_hamburger.setText("☰")
            btn_hamburger.setStyleSheet(
                "background: transparent; border: none; padding: 14px; "
                "color: white; font-size: 20px;"
            )
        btn_hamburger.clicked.connect(self.toggle_sidebar)
        menu_layout.addWidget(btn_hamburger)

        # ------------- انتخابگر زبان -------------
        self.cmb_language = QComboBox()
        for code, info in SUPPORTED_LANGUAGES.items():
            self.cmb_language.addItem(info["label"], code)
        idx = self.cmb_language.findData(get_language())
        if idx >= 0:
            self.cmb_language.setCurrentIndex(idx)
        self.cmb_language.currentIndexChanged.connect(self.change_language)
        menu_layout.addWidget(self.cmb_language)

        self.brand_label = QLabel("DIMA")
        self.brand_label.setStyleSheet("color: #d4af37; font-size: 22px; font-weight: bold; padding: 20px;")
        self.brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menu_layout.addWidget(self.brand_label)

        self.user_label = QLabel(f"{self.auth.current_user['full_name']}")
        self.user_label.setStyleSheet("color: #ffffff; padding: 4px 20px; font-size: 12px;")
        self.user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        menu_layout.addWidget(self.user_label)
        menu_layout.addSpacing(10)

        self.stacked_widget = QStackedWidget()

        self.pages = {
            "dashboard": DashboardPage(),
            "sales": SalesPage(),
            "purchase": PurchasePage(),
            "customers": CustomersPage(),
            "invoices": InvoicesPage(),
            "treasury": TreasuryPage(),
            "checks": ChecksPage(),
        }

        # (متن نمایشی، کلید صفحه، آیکون، کلید ترجمه) — متن نمایشی برای اولین
        # رسم استفاده می‌شود و retranslate_ui بعداً طبق کلید ترجمه به‌روزش می‌کند.
        menu_items = [
            (tr("menu_dashboard"), "dashboard", "fa5s.home", "menu_dashboard"),
            (tr("menu_sales"), "sales", "fa5s.shopping-cart", "menu_sales"),
            (tr("menu_purchase"), "purchase", "fa5s.truck", "menu_purchase"),
            (tr("menu_customers"), "customers", "fa5s.address-book", "menu_customers"),
            (tr("menu_invoices"), "invoices", "fa5s.file-invoice", "menu_invoices"),
            (tr("menu_treasury"), "treasury", "fa5s.money-bill-wave", "menu_treasury"),
            (tr("menu_checks"), "checks", "fa5s.money-check-alt", "menu_checks"),
        ]

        # مدیریت کالا، قیمت‌ها و گروه‌بندی: طبق قانون دسترسی، فقط برای
        # «مدیر فروشگاه» (admin) و «حسابدار» (accountant) در منو نمایش داده می‌شود.
        # صندوق‌دار اصلاً این گزینه را در منوی خودش نمی‌بیند.
        if self.auth.can_manage_products():
            self.pages["inventory"] = InventoryPage()
            menu_items.insert(3, (tr("menu_inventory"), "inventory", "fa5s.boxes", "menu_inventory"))

            # ماژول حسابداری کامل (سرفصل حسابها، دفتر کل، ترازنامه، سود و زیان،
            # اسناد مودیان) نیز فقط برای مدیر و حسابدار در دسترس است.
            self.pages["accounting"] = AccountingPage()
            menu_items.append((tr("menu_accounting"), "accounting", "fa5s.calculator", "menu_accounting"))

        # ماژول تنظیمات (مدیریت کاربران و صندوق‌ها) فقط برای ادمین بارگذاری می‌شود
        if self.auth.is_admin():
            self.pages["settings"] = SettingsPage()
            menu_items.append((tr("menu_settings"), "settings", "fa5s.cog", "menu_settings"))

        # صفحه‌ی «درباره» برای همه‌ی نقش‌ها در دسترس است و همیشه انتهای منو می‌آید
        self.pages["about"] = AboutPage()
        menu_items.append((tr("menu_about"), "about", "fa5s.info-circle", "menu_about"))

        # ------------- ساخت دکمه‌های منو با SidebarButton (متن/آیکون واقعاً نمایش داده می‌شود) -------------
        self.menu_buttons = {}
        self.menu_text_labels = {}
        self.menu_translation_keys = {}
        for label, key, icon_name, translation_key in menu_items:
            btn = SidebarButton(label, icon_name)
            btn.clicked.connect(lambda k=key: self.switch_page(k))
            menu_layout.addWidget(btn)
            self.menu_buttons[key] = btn
            self.menu_text_labels[key] = btn.text_label
            self.menu_translation_keys[key] = translation_key
            self.stacked_widget.addWidget(self.pages[key])

        menu_layout.addStretch()

        self.btn_logout = SidebarButton(tr("menu_logout"), "fa5s.sign-out-alt", danger=True)
        self.btn_logout.clicked.connect(self.handle_logout)
        self.logout_text_label = self.btn_logout.text_label
        menu_layout.addWidget(self.btn_logout)

        main_layout.addWidget(self.side_menu)
        main_layout.addWidget(self.stacked_widget)

        self.setStatusBar(QStatusBar())
        self.switch_page("dashboard")

    def toggle_sidebar(self):
        """
        جمع‌کردن/بازکردن سایدبار (منوی همبرگری، ریسپانسیو).
        در حالت جمع‌شده فقط آیکون‌ها دیده می‌شوند و عرض سایدبار کم می‌شود؛
        در حالت باز، متن هر گزینه هم دوباره نمایش داده می‌شود.
        """
        self.sidebar_expanded = not self.sidebar_expanded
        new_width = 220 if self.sidebar_expanded else 60
        self.side_menu.setFixedWidth(new_width)

        self.brand_label.setVisible(self.sidebar_expanded)
        self.user_label.setVisible(self.sidebar_expanded)

        for text_label in self.menu_text_labels.values():
            text_label.setVisible(self.sidebar_expanded)
        self.logout_text_label.setVisible(self.sidebar_expanded)

    def switch_page(self, key):
        self.stacked_widget.setCurrentWidget(self.pages[key])
        for k, btn in self.menu_buttons.items():
            btn.setChecked(k == key)
        self._update_status_bar()

    def _update_status_bar(self):
        role_translation_keys = {"admin": "role_admin", "accountant": "role_accountant", "cashier": "role_cashier"}
        role_key = role_translation_keys.get(self.auth.current_user["role"])
        role_display = tr(role_key) if role_key else ""
        self.statusBar().showMessage(
            tr("status_bar_user", name=self.auth.current_user["full_name"], role=role_display)
        )

    def change_language(self):
        """
        تغییر زبان جاری برنامه و ذخیره‌ی دائمی آن در دیتابیس (تا بین اجراهای
        بعدی حفظ شود). همه‌ی صفحاتی که retranslate_ui دارند بلافاصله به‌روز می‌شوند.
        """
        language_code = self.cmb_language.currentData()
        set_language(language_code)
        AppSettingsModule().save_language(language_code)
        self.retranslate_ui()

    def retranslate_ui(self):
        direction = get_layout_direction()
        self.setLayoutDirection(direction)
        self.setWindowTitle(tr("app_title"))

        self.brand_label.setText(tr("brand"))
        self.user_label.setText(self.auth.current_user["full_name"])
        self.logout_text_label.setText(tr("menu_logout"))

        for key, translation_key in self.menu_translation_keys.items():
            self.menu_text_labels[key].setText(tr(translation_key))

        self._update_status_bar()

        # هر صفحه‌ای که متد retranslate_ui داشته باشد (یعنی به i18n مجهز شده)
        # صدا زده می‌شود؛ صفحاتی که هنوز مجهز نشده‌اند نادیده گرفته می‌شوند.
        for page in self.pages.values():
            if hasattr(page, "retranslate_ui"):
                page.retranslate_ui()

    def handle_logout(self):
        self.auth.logout()
        self.logged_out.emit()
        self.close()
