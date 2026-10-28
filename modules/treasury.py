# -*- coding: utf-8 -*-
"""
modules/treasury.py
---------------------
منطق تجاری خزانه: ثبت دریافت/پرداخت نقدی، متصل به فاکتورها و صندوق فعال کاربر.
"""

import datetime
from core.db_manager import DBManager
from modules.accounting import AccountingModule


class TreasuryModule:
    def __init__(self):
        self.db = DBManager.instance()
        self.accounting = AccountingModule()

    def register_transaction(self, trans_type, amount, box_id, user_id,
                              party_id=None, invoice_id=None, description="",
                              skip_accounting=False):
        """
        ثبت یک تراکنش دریافت/پرداخت.
        trans_type: 'receive' (دریافت وجه) یا 'pay' (پرداخت وجه)
        در صورت اتصال به یک شخص (party_id)، مانده حساب طرف نیز به‌روزرسانی می‌شود:
            - دریافت از مشتری  -> کاهش بدهی مشتری (balance کم می‌شود)
            - پرداخت به تامین‌کننده -> کاهش بدهی ما به تامین‌کننده

        skip_accounting: وقتی True باشد، سند حسابداری خودکار صادر نمی‌شود.
            این پارامتر توسط ماژول‌های فروش/خرید استفاده می‌شود، چون آن‌ها خودشان
            قبلاً سند حسابداری فاکتور را صادر کرده‌اند و اگر اینجا هم صادر شود،
            سند تکراری (دوبار شمارش) در دفاتر ایجاد می‌شود.
        """
        today_str = datetime.date.today().strftime("%Y%m%d")

        with self.db.transaction() as cur:
            cur.execute(
                """INSERT INTO treasury_transactions
                   (trans_type, amount, date, box_id, party_id, invoice_id,
                    description, user_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                (trans_type, amount, today_str, box_id, party_id, invoice_id,
                 description, user_id),
            )
            trans_id = cur.lastrowid

            if party_id:
                if trans_type == "receive":
                    # دریافت وجه از مشتری => بدهی مشتری کاهش می‌یابد
                    cur.execute(
                        "UPDATE parties SET balance = balance - ? WHERE id = ?;",
                        (amount, party_id),
                    )
                else:
                    # پرداخت وجه به تامین‌کننده => بدهی ما کاهش می‌یابد
                    cur.execute(
                        "UPDATE parties SET balance = balance + ? WHERE id = ?;",
                        (amount, party_id),
                    )

        # صدور خودکار سند حسابداری بابت این تراکنش خزانه
        # (در صورت نبود نگاشت حساب، بی‌صدا رد می‌شود تا مانع ثبت تراکنش نشود)
        if not skip_accounting:
            try:
                self.accounting.auto_post_treasury_transaction(
                    trans_id, trans_type, amount, user_id, description
                )
            except Exception:
                pass

        return trans_id

    def get_box_balance(self, box_id):
        """محاسبه مانده نقدی صندوق: مجموع دریافت‌ها منهای مجموع پرداخت‌ها."""
        row = self.db.fetch_one(
            """SELECT
                 COALESCE(SUM(CASE WHEN trans_type = 'receive' THEN amount ELSE 0 END), 0) -
                 COALESCE(SUM(CASE WHEN trans_type = 'pay' THEN amount ELSE 0 END), 0) AS balance
               FROM treasury_transactions
               WHERE box_id = ?;""",
            (box_id,),
        )
        return row["balance"]

    def get_transactions(self, box_id=None):
        if box_id is None:
            return self.db.fetch_all(
                "SELECT * FROM treasury_transactions ORDER BY id DESC;"
            )
        return self.db.fetch_all(
            "SELECT * FROM treasury_transactions WHERE box_id = ? ORDER BY id DESC;",
            (box_id,),
        )
