# -*- coding: utf-8 -*-
"""
modules/checks.py
--------------------
مدیریت چک‌های دریافتی (از مشتریان) و پرداختی (به تامین‌کنندگان).
وصول/برگشت/انتقال چک به‌صورت خودکار در خزانه و حسابداری ثبت می‌شود.
"""

import datetime
from core.db_manager import DBManager
from modules.treasury import TreasuryModule
from modules.accounting import AccountingModule


class CheckModule:
    def __init__(self):
        self.db = DBManager.instance()
        self.treasury = TreasuryModule()
        self.accounting = AccountingModule()

    def register_check(self, check_number, bank_name, amount, due_date,
                        direction, party_id, box_id, user_id, description=""):
        """
        ثبت یک چک جدید.
        direction: 'received' (چک دریافتی از مشتری) یا 'issued' (چک صادرشده به تامین‌کننده)
        """
        created_date = datetime.date.today().strftime("%Y%m%d")
        return self.db.execute(
            """INSERT INTO checks
               (check_number, bank_name, amount, due_date, direction, status,
                party_id, box_id, description, user_id, created_date)
               VALUES (?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?);""",
            (check_number, bank_name, amount, due_date, direction,
             party_id, box_id, description, user_id, created_date),
        )

    def get_checks(self, status=None, box_id=None):
        query = "SELECT * FROM checks WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if box_id is not None:
            query += " AND box_id = ?"
            params.append(box_id)
        query += " ORDER BY due_date;"
        return self.db.fetch_all(query, tuple(params))

    def mark_collected(self, check_id, user_id):
        """
        وصول چک: مبلغ چک به‌صورت خودکار به عنوان «دریافت وجه» در خزانه
        و سند حسابداری مرتبط ثبت می‌شود.
        """
        check = self.db.fetch_one("SELECT * FROM checks WHERE id = ?;", (check_id,))
        if check is None:
            raise ValueError("چک یافت نشد.")
        if check["status"] != "pending":
            raise ValueError("این چک قبلاً تسویه یا برگشت خورده است.")

        self.db.execute("UPDATE checks SET status = 'collected' WHERE id = ?;", (check_id,))

        if check["direction"] == "received":
            self.treasury.register_transaction(
                trans_type="receive", amount=check["amount"], box_id=check["box_id"],
                user_id=user_id, party_id=check["party_id"],
                description=f"وصول چک شماره {check['check_number']}",
            )
        else:
            self.treasury.register_transaction(
                trans_type="pay", amount=check["amount"], box_id=check["box_id"],
                user_id=user_id, party_id=check["party_id"],
                description=f"پرداخت چک شماره {check['check_number']}",
            )

    def mark_bounced(self, check_id):
        """ثبت برگشت خوردن چک (بدون اثر مالی در خزانه)."""
        check = self.db.fetch_one("SELECT * FROM checks WHERE id = ?;", (check_id,))
        if check is None:
            raise ValueError("چک یافت نشد.")
        if check["status"] != "pending":
            raise ValueError("این چک قبلاً تسویه یا برگشت خورده است.")
        self.db.execute("UPDATE checks SET status = 'bounced' WHERE id = ?;", (check_id,))

    def update_check(self, check_id, check_number, bank_name, amount, due_date, description=""):
        """
        ویرایش اطلاعات یک چک.
        فقط روی چک‌های «در انتظار وصول» مجاز است؛ چون تغییر مبلغ/تاریخ یک چک
        که قبلاً وصول یا برگشت خورده، با تراکنش خزانه/سند حسابداری قبلاً ثبت‌شده
        هماهنگ نمی‌ماند.
        """
        check = self.db.fetch_one("SELECT * FROM checks WHERE id = ?;", (check_id,))
        if check is None:
            raise ValueError("چک یافت نشد.")
        if check["status"] != "pending":
            raise ValueError("فقط چک‌های «در انتظار وصول» قابل ویرایش هستند.")
        self.db.execute(
            """UPDATE checks
               SET check_number = ?, bank_name = ?, amount = ?, due_date = ?, description = ?
               WHERE id = ?;""",
            (check_number, bank_name, amount, due_date, description, check_id),
        )

    def delete_check(self, check_id):
        """
        حذف یک چک.
        فقط روی چک‌های «در انتظار وصول» مجاز است؛ چک‌های وصول‌شده حذف نمی‌شوند
        چون تراکنش خزانه و سند حسابداری مرتبط با آن‌ها قبلاً ثبت شده و حذف چک
        باعث ناهماهنگی دفاتر می‌شود.
        """
        check = self.db.fetch_one("SELECT * FROM checks WHERE id = ?;", (check_id,))
        if check is None:
            raise ValueError("چک یافت نشد.")
        if check["status"] != "pending":
            raise ValueError("فقط چک‌های «در انتظار وصول» قابل حذف هستند.")
        self.db.execute("DELETE FROM checks WHERE id = ?;", (check_id,))
