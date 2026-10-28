# -*- coding: utf-8 -*-
"""
core/db_manager.py
-------------------
مدیریت اتصال به دیتابیس SQLite با الگوی Singleton.
این کلاس مسئول موارد زیر است:
    - ایجاد و مقداردهی اولیه (Seed) دیتابیس در اولین اجرا
    - فراهم کردن متدهای CRUD عمومی (Repository Pattern) برای تمام ماژول‌ها
    - مدیریت تراکنش‌ها (BEGIN / COMMIT / ROLLBACK) برای عملیات حساس مانند ثبت فاکتور

نکته معماری:
    هیچ کلاس دیگری در پروژه نباید مستقیماً sqlite3.connect را صدا بزند؛
    همه باید از طریق DBManager.instance() کار کنند تا یکپارچگی و تک‌نمونه بودن
    اتصال دیتابیس حفظ شود.
"""

import sqlite3
import sys
import os
import hashlib
import binascii
from contextlib import contextmanager

DB_FILE_NAME = "dima_accounting.db"


class DBManager:
    """
    کلاس Singleton برای مدیریت اتصال به SQLite.
    استفاده:
        db = DBManager.instance()
        rows = db.fetch_all("SELECT * FROM products")
    """

    _instance = None

    # ---------------------------------------------------------------
    # Singleton Pattern
    # ---------------------------------------------------------------
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = None):
        if self._initialized:
            return
        # نکته حیاتی برای نسخه‌ی نصبی (PyInstaller):
        # وقتی برنامه فریز/بسته‌بندی شده باشد (sys.frozen == True)، نباید از
        # مسیر این فایل پایتون (که داخل پوشه‌ی موقت استخراج‌شده قرار دارد)
        # استفاده کرد؛ وگرنه دیتابیس هر بار در یک پوشه‌ی موقت جدید ساخته شده
        # و با بستن برنامه از بین می‌رود. در این حالت باید کنار خودِ فایل .exe
        # (sys.executable) ذخیره شود تا بین اجراهای مختلف برنامه پایدار بماند.
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = db_path or os.path.join(base_dir, DB_FILE_NAME)
        self.connection = None
        self._connect()
        self._create_schema()
        self._seed_initial_data()
        self._initialized = True

    @classmethod
    def instance(cls):
        """دسترسی سراسری به نمونه‌ی یکتای DBManager."""
        if cls._instance is None:
            cls._instance = DBManager()
        return cls._instance

    # ---------------------------------------------------------------
    # اتصال پایه
    # ---------------------------------------------------------------
    def _connect(self):
        # فعال‌سازی foreign_keys ضروری است چون SQLite به صورت پیش‌فرض آن را غیرفعال می‌کند
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON;")

    @contextmanager
    def transaction(self):
        """
        مدیریت تراکنش امن.
        استفاده:
            with db.transaction() as cur:
                cur.execute(...)
                cur.execute(...)
        در صورت بروز خطا، ROLLBACK خودکار انجام می‌شود؛
        در صورت موفقیت، COMMIT در پایان بلاک انجام می‌شود.
        این متد اصلی‌ترین ابزار برای ثبت فاکتور (هدر + اقلام) به صورت یکپارچه است.
        """
        cur = self.connection.cursor()
        try:
            cur.execute("BEGIN TRANSACTION;")
            yield cur
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cur.close()

    # ---------------------------------------------------------------
    # متدهای عمومی CRUD (Repository Pattern پایه)
    # ---------------------------------------------------------------
    def execute(self, query: str, params: tuple = ()):
        """اجرای یک کوئری تکی (INSERT/UPDATE/DELETE) خارج از تراکنش دستی."""
        cur = self.connection.cursor()
        cur.execute(query, params)
        self.connection.commit()
        last_id = cur.lastrowid
        cur.close()
        return last_id

    def fetch_all(self, query: str, params: tuple = ()):
        """اجرای SELECT و بازگرداندن تمام سطرها به صورت list[sqlite3.Row]."""
        cur = self.connection.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        return rows

    def fetch_one(self, query: str, params: tuple = ()):
        """اجرای SELECT و بازگرداندن یک سطر یا None."""
        cur = self.connection.cursor()
        cur.execute(query, params)
        row = cur.fetchone()
        cur.close()
        return row

    def close(self):
        if self.connection:
            self.connection.close()

    # ---------------------------------------------------------------
    # ساخت اسکیمای دیتابیس
    # ---------------------------------------------------------------
    def _create_schema(self):
        """
        ایجاد تمام جداول در صورت عدم وجود.
        از IF NOT EXISTS استفاده شده تا اجرای مجدد برنامه خطا ندهد.
        """
        schema_statements = [
            # ---------------- صندوق‌های صندوق‌داری ----------------
            """
            CREATE TABLE IF NOT EXISTS cash_boxes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL UNIQUE,
                is_active   INTEGER NOT NULL DEFAULT 1
            );
            """,
            # ---------------- کاربران ----------------
            """
            CREATE TABLE IF NOT EXISTS users (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                username        TEXT NOT NULL UNIQUE,
                password_hash   TEXT NOT NULL,
                salt            TEXT NOT NULL,
                full_name       TEXT NOT NULL,
                role            TEXT NOT NULL CHECK(role IN ('admin', 'accountant', 'cashier')),
                box_id          INTEGER,
                is_active       INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (box_id) REFERENCES cash_boxes(id) ON DELETE SET NULL
            );
            """,
            # ---------------- گروه‌بندی کالا (گروه اصلی / زیرگروه) ----------------
            """
            CREATE TABLE IF NOT EXISTS product_categories (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                parent_id   INTEGER,
                FOREIGN KEY (parent_id) REFERENCES product_categories(id) ON DELETE CASCADE
            );
            """,
            # ---------------- برچسب سطوح قیمت (مثلاً قیمت قدیم/جدید/عمده/نقدی) ----------------
            # فقط حسابدار و مدیر فروشگاه اجازه ویرایش این برچسب‌ها را دارند (کنترل در لایه UI/Auth).
            """
            CREATE TABLE IF NOT EXISTS price_tier_labels (
                tier_number INTEGER PRIMARY KEY CHECK(tier_number BETWEEN 1 AND 4),
                label       TEXT NOT NULL
            );
            """,
            # ---------------- کالاها ----------------
            """
            CREATE TABLE IF NOT EXISTS products (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode         TEXT UNIQUE,
                code            TEXT NOT NULL UNIQUE,
                name            TEXT NOT NULL,
                unit_type       TEXT NOT NULL DEFAULT 'عدد',
                units_per_box   INTEGER NOT NULL DEFAULT 1,
                buy_price       REAL NOT NULL DEFAULT 0,
                sell_price_1    REAL NOT NULL DEFAULT 0,
                sell_price_2    REAL NOT NULL DEFAULT 0,
                sell_price_3    REAL NOT NULL DEFAULT 0,
                sell_price_4    REAL NOT NULL DEFAULT 0,
                group_main_id   INTEGER,
                group_sub_id    INTEGER,
                stock_qty       REAL NOT NULL DEFAULT 0,
                min_stock       REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (group_main_id) REFERENCES product_categories(id) ON DELETE SET NULL,
                FOREIGN KEY (group_sub_id) REFERENCES product_categories(id) ON DELETE SET NULL
            );
            """,
            # ---------------- اشخاص (مشتری/تامین‌کننده) ----------------
            """
            CREATE TABLE IF NOT EXISTS parties (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                type    TEXT NOT NULL CHECK(type IN ('customer', 'supplier')),
                phone   TEXT,
                balance REAL NOT NULL DEFAULT 0
            );
            """,
            # ---------------- فاکتورها (هدر) ----------------
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number      TEXT NOT NULL UNIQUE,
                invoice_type        TEXT NOT NULL CHECK(invoice_type IN ('sale', 'purchase')),
                date                TEXT NOT NULL,
                party_id            INTEGER,
                user_id             INTEGER NOT NULL,
                box_id              INTEGER NOT NULL,
                subtotal_amount     REAL NOT NULL DEFAULT 0,
                discount_amount     REAL NOT NULL DEFAULT 0,
                discount_type       TEXT NOT NULL DEFAULT 'rial' CHECK(discount_type IN ('rial', 'percent')),
                tax_amount          REAL NOT NULL DEFAULT 0,
                duty_amount         REAL NOT NULL DEFAULT 0,
                total_amount        REAL NOT NULL DEFAULT 0,
                payment_type        TEXT NOT NULL DEFAULT 'cash',
                is_wholesale        INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (party_id) REFERENCES parties(id) ON DELETE SET NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (box_id) REFERENCES cash_boxes(id)
            );
            """,
            # ---------------- اقلام فاکتور ----------------
            """
            CREATE TABLE IF NOT EXISTS invoice_items (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id      INTEGER NOT NULL,
                product_id      INTEGER NOT NULL,
                qty_num         REAL NOT NULL DEFAULT 0,
                qty_box         REAL NOT NULL DEFAULT 0,
                gift_qty        REAL NOT NULL DEFAULT 0,
                prod_date       TEXT,
                exp_date        TEXT,
                price           REAL NOT NULL DEFAULT 0,
                price_tier      INTEGER,
                discount_amount REAL NOT NULL DEFAULT 0,
                discount_type   TEXT NOT NULL DEFAULT 'rial' CHECK(discount_type IN ('rial', 'percent')),
                has_tax         INTEGER NOT NULL DEFAULT 0,
                tax_percent     REAL NOT NULL DEFAULT 0,
                tax_amount      REAL NOT NULL DEFAULT 0,
                line_total      REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
            """,
            # ---------------- خزانه‌داری (دریافت / پرداخت) ----------------
            """
            CREATE TABLE IF NOT EXISTS treasury_transactions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                trans_type      TEXT NOT NULL CHECK(trans_type IN ('receive', 'pay')),
                amount          REAL NOT NULL,
                date            TEXT NOT NULL,
                box_id          INTEGER NOT NULL,
                party_id        INTEGER,
                invoice_id      INTEGER,
                description     TEXT,
                user_id         INTEGER NOT NULL,
                FOREIGN KEY (box_id) REFERENCES cash_boxes(id),
                FOREIGN KEY (party_id) REFERENCES parties(id),
                FOREIGN KEY (invoice_id) REFERENCES invoices(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """,
            # ================= ماژول حسابداری (سرفصل حسابها و اسناد) =================
            # ---------------- سرفصل حسابها ----------------
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                code            TEXT NOT NULL UNIQUE,
                name            TEXT NOT NULL,
                account_type    TEXT NOT NULL CHECK(account_type IN
                                 ('asset', 'liability', 'equity', 'revenue', 'expense')),
                parent_id       INTEGER,
                is_active       INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (parent_id) REFERENCES accounts(id) ON DELETE SET NULL
            );
            """,
            # ---------------- اسناد حسابداری (هدر سند) ----------------
            """
            CREATE TABLE IF NOT EXISTS journal_entries (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_number    TEXT NOT NULL UNIQUE,
                date            TEXT NOT NULL,
                description     TEXT,
                user_id         INTEGER NOT NULL,
                source_type     TEXT NOT NULL DEFAULT 'manual'
                                 CHECK(source_type IN ('manual', 'sale', 'purchase', 'treasury', 'check')),
                source_id       INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """,
            # ---------------- ردیف‌های سند (بدهکار/بستانکار) ----------------
            """
            CREATE TABLE IF NOT EXISTS journal_entry_lines (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id    INTEGER NOT NULL,
                account_id  INTEGER NOT NULL,
                debit       REAL NOT NULL DEFAULT 0,
                credit      REAL NOT NULL DEFAULT 0,
                description TEXT,
                FOREIGN KEY (entry_id) REFERENCES journal_entries(id) ON DELETE CASCADE,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );
            """,
            # ---------------- تنظیمات نگاشت حساب پیش‌فرض (برای صدور خودکار سند) ----------------
            """
            CREATE TABLE IF NOT EXISTS account_mappings (
                mapping_key TEXT PRIMARY KEY,
                account_id  INTEGER,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );
            """,
            # ================= چک‌ها (دریافتی/پرداختی) =================
            """
            CREATE TABLE IF NOT EXISTS checks (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                check_number    TEXT NOT NULL,
                bank_name       TEXT,
                amount          REAL NOT NULL,
                due_date        TEXT NOT NULL,
                direction       TEXT NOT NULL CHECK(direction IN ('received', 'issued')),
                status          TEXT NOT NULL DEFAULT 'pending'
                                 CHECK(status IN ('pending', 'collected', 'bounced', 'transferred')),
                party_id        INTEGER,
                box_id          INTEGER NOT NULL,
                description     TEXT,
                user_id         INTEGER NOT NULL,
                created_date    TEXT NOT NULL,
                FOREIGN KEY (party_id) REFERENCES parties(id),
                FOREIGN KEY (box_id) REFERENCES cash_boxes(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """,
            # ================= اسناد ارسال به سامانه مودیان (ساختار داده - بدون اتصال API واقعی) =================
            """
            CREATE TABLE IF NOT EXISTS modian_invoices (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id      INTEGER NOT NULL UNIQUE,
                tax_id          TEXT,
                uid             TEXT,
                status          TEXT NOT NULL DEFAULT 'not_prepared'
                                 CHECK(status IN ('not_prepared', 'ready', 'sent', 'confirmed', 'failed')),
                payload_json    TEXT,
                prepared_at     TEXT,
                sent_at         TEXT,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
            );
            """,
            # ---------------- تنظیمات اتصال به سامانه مودیان (لینک API و گواهی دیجیتال) ----------------
            """
            CREATE TABLE IF NOT EXISTS modian_settings (
                id                  INTEGER PRIMARY KEY CHECK (id = 1),
                api_url             TEXT,
                certificate_path    TEXT
            );
            """,
            # ---------------- تنظیمات دستگاه بارکدخوان (USB کیبوردی یا سریال COM) ----------------
            """
            CREATE TABLE IF NOT EXISTS scanner_settings (
                id          INTEGER PRIMARY KEY CHECK (id = 1),
                mode        TEXT NOT NULL DEFAULT 'usb' CHECK(mode IN ('usb', 'serial')),
                port        TEXT,
                baud_rate   INTEGER NOT NULL DEFAULT 9600
            );
            """,
            # ---------------- تنظیمات سرویس پیامک (قابل تعویض بدون تغییر کد) ----------------
            """
            CREATE TABLE IF NOT EXISTS sms_settings (
                id                  INTEGER PRIMARY KEY CHECK (id = 1),
                provider            TEXT NOT NULL DEFAULT 'generic',
                api_url             TEXT,
                api_key             TEXT,
                sender_number       TEXT,
                http_method         TEXT NOT NULL DEFAULT 'POST',
                payload_template    TEXT
            );
            """,
            # ---------------- لاگ پیامک‌های ارسالی (برای پیگیری/گزارش) ----------------
            """
            CREATE TABLE IF NOT EXISTS sms_log (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                phone               TEXT NOT NULL,
                message             TEXT NOT NULL,
                status              TEXT NOT NULL DEFAULT 'queued',
                response_snippet    TEXT,
                sent_at             TEXT NOT NULL,
                user_id             INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """,
            # ---------------- تنظیمات عمومی برنامه (فعلاً فقط زبان انتخابی رابط کاربری) ----------------
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                id          INTEGER PRIMARY KEY CHECK (id = 1),
                language    TEXT NOT NULL DEFAULT 'fa'
            );
            """,
        ]

        with self.transaction() as cur:
            for stmt in schema_statements:
                cur.execute(stmt)

    # ---------------------------------------------------------------
    # هش کردن رمز عبور (PBKDF2-HMAC-SHA256 + Salt تصادفی)
    # ---------------------------------------------------------------
    @staticmethod
    def hash_password(password: str, salt: bytes = None):
        if salt is None:
            salt = os.urandom(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 100_000
        )
        return binascii.hexlify(pwd_hash).decode(), binascii.hexlify(salt).decode()

    # ---------------------------------------------------------------
    # مقداردهی اولیه (Seed) - فقط اگر دیتابیس خالی باشد
    # ---------------------------------------------------------------
    def _seed_initial_data(self):
        # صرف‌نظر از اینکه کاربری وجود دارد یا نه (نصب جدید یا ارتقای نسخه قبلی)،
        # همیشه مطمئن می‌شویم برچسب‌های ۴ سطح قیمت و سرفصل حسابهای پایه موجود باشند.
        self._ensure_price_tier_labels()
        self._ensure_sms_tables_upgraded()
        self._ensure_default_accounts()
        self._ensure_default_categories()

        row = self.fetch_one("SELECT COUNT(*) AS c FROM users;")
        if row["c"] > 0:
            return  # دیتابیس قبلاً مقداردهی شده است

        with self.transaction() as cur:
            # ایجاد صندوق پیش‌فرض
            cur.execute(
                "INSERT INTO cash_boxes (name, is_active) VALUES (?, 1);",
                ("صندوق اصلی",),
            )
            main_box_id = cur.lastrowid

            # ایجاد کاربر ادمین پیش‌فرض (admin / admin123)
            pwd_hash, salt = self.hash_password("admin123")
            cur.execute(
                """INSERT INTO users
                   (username, password_hash, salt, full_name, role, box_id, is_active)
                   VALUES (?, ?, ?, ?, ?, ?, 1);""",
                ("admin", pwd_hash, salt, "مدیر سیستم", "admin", main_box_id),
            )

    def _ensure_default_accounts(self):
        """
        ایجاد سرفصل حسابهای پایه (در صورت نبود) و نگاشت خودکار آن‌ها به مفاهیم
        اصلی (صندوق، فروش، خرید، مالیات و ...) تا صدور سند خودکار برای فاکتورها
        و تراکنش‌های خزانه از همان ابتدا کار کند. حسابدار/مدیر بعداً می‌توانند
        سرفصل‌های بیشتری اضافه یا نگاشت‌ها را تغییر دهند.
        """
        existing = self.fetch_one("SELECT COUNT(*) AS c FROM accounts;")
        if existing["c"] > 0:
            return

        default_accounts = [
            # (کد، نام، نوع)
            ("1000", "صندوق", "asset"),
            ("1100", "حسابهای دریافتنی (بدهکاران)", "asset"),
            ("1200", "موجودی کالا", "asset"),
            ("2000", "حسابهای پرداختنی (بستانکاران)", "liability"),
            ("2100", "مالیات بر ارزش افزوده پرداختنی", "liability"),
            ("3000", "سرمایه", "equity"),
            ("4000", "فروش کالا", "revenue"),
            ("5000", "بهای تمام‌شده کالای فروش‌رفته", "expense"),
            ("5100", "خرید کالا", "expense"),
            ("5200", "تخفیفات فروش", "expense"),
        ]

        with self.transaction() as cur:
            code_to_id = {}
            for code, name, acc_type in default_accounts:
                cur.execute(
                    "INSERT INTO accounts (code, name, account_type) VALUES (?, ?, ?);",
                    (code, name, acc_type),
                )
                code_to_id[code] = cur.lastrowid

            mappings = {
                "cash": code_to_id["1000"],
                "accounts_receivable": code_to_id["1100"],
                "inventory": code_to_id["1200"],
                "accounts_payable": code_to_id["2000"],
                "vat_payable": code_to_id["2100"],
                "sales_revenue": code_to_id["4000"],
                "cogs": code_to_id["5000"],
                "purchase_expense": code_to_id["5100"],
                "sales_discount": code_to_id["5200"],
            }
            for key, account_id in mappings.items():
                cur.execute(
                    "INSERT INTO account_mappings (mapping_key, account_id) VALUES (?, ?);",
                    (key, account_id),
                )

    def _ensure_price_tier_labels(self):
        """درج برچسب پیش‌فرض برای هر سطح قیمت که هنوز برچسبی ندارد (idempotent)."""
        default_labels = {
            1: "قیمت نقدی",
            2: "قیمت نسیه",
            3: "قیمت قدیم",
            4: "قیمت جدید",
        }
        existing = self.fetch_all("SELECT tier_number FROM price_tier_labels;")
        existing_tiers = {row["tier_number"] for row in existing}

        missing = [(tier, label) for tier, label in default_labels.items() if tier not in existing_tiers]
        if missing:
            with self.transaction() as cur:
                cur.executemany(
                    "INSERT INTO price_tier_labels (tier_number, label) VALUES (?, ?);",
                    missing,
                )

    def _ensure_sms_tables_upgraded(self):
        """
        ارتقای امن جدول‌های sms_settings/sms_log برای دیتابیس‌هایی که با نسخه‌ی
        قدیمی‌تر ساخته شده‌اند (که فقط api_key/sender_number داشتند). با ALTER
        TABLE ستون‌های جدید (نوع سرویس‌دهنده، آدرس API، روش HTTP، قالب پیام)
        اضافه می‌شود تا اطلاعات قبلی کاربر از بین نرود.
        """
        sms_settings_migrations = {
            "provider": "TEXT NOT NULL DEFAULT 'generic'",
            "api_url": "TEXT",
            "http_method": "TEXT NOT NULL DEFAULT 'POST'",
            "payload_template": "TEXT",
        }
        existing_cols = {row["name"] for row in self.fetch_all("PRAGMA table_info(sms_settings);")}
        for col, col_def in sms_settings_migrations.items():
            if col not in existing_cols:
                self.execute(f"ALTER TABLE sms_settings ADD COLUMN {col} {col_def};")

        existing_log_cols = {row["name"] for row in self.fetch_all("PRAGMA table_info(sms_log);")}
        if "response_snippet" not in existing_log_cols:
            self.execute("ALTER TABLE sms_log ADD COLUMN response_snippet TEXT;")

    def _ensure_default_categories(self):
        """
        ایجاد چند گروه اصلی و زیرگروه پیش‌فرض رایج در فروشگاه‌ها (در صورت نبود)
        تا کاربر مجبور نباشد از صفر گروه‌بندی بسازد؛ همچنان می‌تواند از دکمه‌ی
        «+ گروه/زیرگروه جدید» در صفحه‌ی انبار، گروه‌های دلخواه خودش را هم اضافه کند.
        """
        existing = self.fetch_one("SELECT COUNT(*) AS c FROM product_categories;")
        if existing["c"] > 0:
            return

        default_structure = {
            "لبنیات": ["شیر و ماست", "پنیر", "بستنی"],
            "خواروبار": ["برنج و حبوبات", "روغن و رب", "کنسرو"],
            "نوشیدنی": ["نوشابه و آبمیوه", "آب معدنی", "چای و قهوه"],
            "بهداشتی": ["شوینده", "آرایشی", "دستمال کاغذی"],
            "سایر": [],
        }

        with self.transaction() as cur:
            for main_name, sub_names in default_structure.items():
                cur.execute(
                    "INSERT INTO product_categories (name, parent_id) VALUES (?, NULL);",
                    (main_name,),
                )
                main_id = cur.lastrowid
                for sub_name in sub_names:
                    cur.execute(
                        "INSERT INTO product_categories (name, parent_id) VALUES (?, ?);",
                        (sub_name, main_id),
                    )
