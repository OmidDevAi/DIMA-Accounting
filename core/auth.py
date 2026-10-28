# -*- coding: utf-8 -*-
"""
core/auth.py
-------------
مدیریت احراز هویت (Authentication) و مجوزها (Authorization).
این ماژول مسئول موارد زیر است:
    - بررسی صحت نام کاربری/رمز عبور هنگام ورود
    - نگهداری اطلاعات کاربر جاری (Session ساده در حافظه)
    - ارائه ابزار کمکی برای بررسی نقش کاربر (ادمین / صندوق‌دار)
"""

import binascii
from core.db_manager import DBManager


class AuthManager:
    """
    مدیریت وضعیت لاگین کاربر جاری.
    از الگوی Singleton ساده استفاده می‌کند تا در کل برنامه یک نمونه از
    "کاربر لاگین‌کرده" وجود داشته باشد و ماژول‌های مختلف (فروش، خرید و ...)
    بتوانند بدون پاس دادن دستی، به current_user دسترسی داشته باشند.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthManager, cls).__new__(cls)
            cls._instance.current_user = None
        return cls._instance

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = AuthManager()
        return cls._instance

    # ---------------------------------------------------------------
    def login(self, username: str, password: str):
        """
        تلاش برای ورود کاربر.
        بازگشت: dict اطلاعات کاربر در صورت موفقیت، در غیر این صورت None.
        """
        db = DBManager.instance()
        user = db.fetch_one(
            "SELECT * FROM users WHERE username = ? AND is_active = 1;",
            (username,),
        )
        if user is None:
            return None

        salt_bytes = binascii.unhexlify(user["salt"])
        computed_hash, _ = DBManager.hash_password(password, salt_bytes)

        if computed_hash != user["password_hash"]:
            return None

        # ذخیره کاربر جاری در حافظه (session)
        self.current_user = {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "box_id": user["box_id"],
        }
        return self.current_user

    def logout(self):
        self.current_user = None

    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def is_admin(self) -> bool:
        return self.is_authenticated() and self.current_user["role"] == "admin"

    def is_accountant(self) -> bool:
        return self.is_authenticated() and self.current_user["role"] == "accountant"

    def can_manage_products(self) -> bool:
        """
        قانون دسترسی: مدیریت قیمت‌ها، گروه‌بندی کالا و برچسب سطوح قیمت
        فقط برای «مدیر فروشگاه» (admin) و «حسابدار» (accountant) مجاز است.
        صندوق‌دار (cashier) فقط اجازه دارد در فاکتور فروش از قیمت‌های
        از پیش تعریف‌شده انتخاب کند، نه اینکه آن‌ها را تغییر دهد.
        """
        return self.is_authenticated() and self.current_user["role"] in ("admin", "accountant")

    def can_send_bulk_sms(self) -> bool:
        """پیامک گروهی به کل لیست مشتریان: فقط مدیر فروشگاه و حسابدار."""
        return self.is_authenticated() and self.current_user["role"] in ("admin", "accountant")

    def can_search_inactive_customers(self) -> bool:
        """جستجوی مشتریان بدون خرید در یک بازه و ارسال پیامک به آن‌ها: فقط مدیر فروشگاه و صندوق‌دار."""
        return self.is_authenticated() and self.current_user["role"] in ("admin", "cashier")

    def get_accessible_box_id(self):
        """
        قانون ایزولاسیون صندوق:
            - ادمین: None برمی‌گرداند به معنی «دسترسی به همه‌ی صندوق‌ها»
            - صندوق‌دار: فقط box_id خودش را برمی‌گرداند
        این متد باید در تمام کوئری‌های ماژول‌ها (فروش/خرید/انبار/خزانه) استفاده شود
        تا فیلتر صندوق به صورت خودکار اعمال شود.
        """
        if not self.is_authenticated():
            return -1  # هیچ دسترسی‌ای وجود ندارد
        if self.current_user["role"] == "admin":
            return None
        return self.current_user["box_id"]

    @staticmethod
    def create_user(username, password, full_name, role, box_id):
        """
        ایجاد کاربر جدید (فقط باید از UI تنظیمات و توسط ادمین صدا زده شود).
        """
        db = DBManager.instance()
        pwd_hash, salt = DBManager.hash_password(password)
        return db.execute(
            """INSERT INTO users
               (username, password_hash, salt, full_name, role, box_id, is_active)
               VALUES (?, ?, ?, ?, ?, ?, 1);""",
            (username, pwd_hash, salt, full_name, role, box_id),
        )

    @staticmethod
    def update_user(user_id, full_name, role, box_id):
        """ویرایش اطلاعات کاربر (نام کامل، نقش، صندوق تخصیصی). رمز عبور جدا تغییر می‌کند."""
        db = DBManager.instance()
        db.execute(
            "UPDATE users SET full_name = ?, role = ?, box_id = ? WHERE id = ?;",
            (full_name, role, box_id, user_id),
        )

    @staticmethod
    def set_user_password(user_id, new_password):
        """تغییر رمز عبور یک کاربر توسط ادمین (بدون نیاز به دانستن رمز قبلی)."""
        db = DBManager.instance()
        pwd_hash, salt = DBManager.hash_password(new_password)
        db.execute(
            "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?;",
            (pwd_hash, salt, user_id),
        )

    @staticmethod
    def set_user_active(user_id, is_active: bool):
        """
        غیرفعال/فعال کردن کاربر (معادل «حذف» ایمن).
        به‌جای حذف واقعی ردیف از جدول users استفاده می‌شود، چون کاربر ممکن
        است در فاکتورها، اسناد حسابداری، تراکنش‌های خزانه و... به‌عنوان
        ثبت‌کننده رفرنس شده باشد؛ حذف واقعی آن ردیف باعث خطای یکپارچگی
        (Foreign Key) یا از دست رفتن تاریخچه‌ی «چه کسی این سند را ثبت کرده»
        می‌شود. کاربر غیرفعال دیگر نمی‌تواند وارد سیستم شود (login آن را رد می‌کند).
        """
        db = DBManager.instance()
        db.execute(
            "UPDATE users SET is_active = ? WHERE id = ?;",
            (1 if is_active else 0, user_id),
        )
