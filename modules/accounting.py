# -*- coding: utf-8 -*-
"""
modules/accounting.py
------------------------
هسته‌ی ماژول حسابداری دو-طرفه (Double-Entry Bookkeeping):
    - سرفصل حسابها (Chart of Accounts)
    - صدور سند حسابداری دستی یا خودکار (از فروش/خرید/خزانه/چک)
    - دفتر کل (مرور گردش هر حساب)
    - تراز آزمایشی (جمع بدهکار/بستانکار هر حساب)
    - سود و زیان (درآمد - هزینه در یک بازه)
    - ترازنامه (مانده حسابهای دارایی/بدهی/سرمایه تا یک تاریخ مشخص)

قانون بنیادی حسابداری دوطرفه: در هر سند، جمع بدهکار باید دقیقاً برابر
جمع بستانکار باشد؛ در غیر این صورت سند رد می‌شود.
"""

import datetime
from core.db_manager import DBManager


class AccountingModule:
    def __init__(self):
        self.db = DBManager.instance()

    # =================================================================
    # سرفصل حسابها
    # =================================================================
    def add_account(self, code, name, account_type, parent_id=None):
        return self.db.execute(
            "INSERT INTO accounts (code, name, account_type, parent_id) VALUES (?, ?, ?, ?);",
            (code, name, account_type, parent_id),
        )

    def get_accounts(self):
        return self.db.fetch_all("SELECT * FROM accounts WHERE is_active = 1 ORDER BY code;")

    def get_account(self, account_id):
        return self.db.fetch_one("SELECT * FROM accounts WHERE id = ?;", (account_id,))

    # =================================================================
    # نگاشت حساب پیش‌فرض (برای صدور خودکار سند)
    # =================================================================
    def get_account_mapping(self, key):
        row = self.db.fetch_one(
            "SELECT account_id FROM account_mappings WHERE mapping_key = ?;", (key,)
        )
        return row["account_id"] if row else None

    def set_account_mapping(self, key, account_id):
        existing = self.db.fetch_one(
            "SELECT mapping_key FROM account_mappings WHERE mapping_key = ?;", (key,)
        )
        if existing:
            self.db.execute(
                "UPDATE account_mappings SET account_id = ? WHERE mapping_key = ?;",
                (account_id, key),
            )
        else:
            self.db.execute(
                "INSERT INTO account_mappings (mapping_key, account_id) VALUES (?, ?);",
                (key, account_id),
            )

    def get_all_mappings(self):
        return self.db.fetch_all("SELECT * FROM account_mappings;")

    # =================================================================
    # صدور سند حسابداری (دستی یا خودکار)
    # =================================================================
    def _generate_entry_number(self):
        today = datetime.date.today().strftime("%Y%m%d")
        row = self.db.fetch_one(
            "SELECT COUNT(*) AS c FROM journal_entries WHERE date LIKE ?;", (f"{today}%",)
        )
        seq = (row["c"] or 0) + 1
        return f"JRN-{today}-{seq:04d}"

    def create_journal_entry(self, description, lines, user_id,
                              source_type="manual", source_id=None, date=None):
        """
        ثبت یک سند حسابداری.
        lines: لیستی از دیکشنری {account_id, debit, credit, description}
        قانون: مجموع بدهکار باید دقیقاً برابر مجموع بستانکار باشد، وگرنه ValueError.
        """
        total_debit = sum(l.get("debit", 0) for l in lines)
        total_credit = sum(l.get("credit", 0) for l in lines)
        if round(total_debit, 2) != round(total_credit, 2):
            raise ValueError(
                f"سند نامتوازن است: جمع بدهکار ({total_debit:,.0f}) با "
                f"جمع بستانکار ({total_credit:,.0f}) برابر نیست."
            )
        if total_debit == 0:
            raise ValueError("سند خالی است؛ حداقل یک ردیف با مبلغ لازم است.")

        entry_number = self._generate_entry_number()
        date_str = date or datetime.date.today().strftime("%Y%m%d")

        with self.db.transaction() as cur:
            cur.execute(
                """INSERT INTO journal_entries
                   (entry_number, date, description, user_id, source_type, source_id)
                   VALUES (?, ?, ?, ?, ?, ?);""",
                (entry_number, date_str, description, user_id, source_type, source_id),
            )
            entry_id = cur.lastrowid

            for line in lines:
                cur.execute(
                    """INSERT INTO journal_entry_lines
                       (entry_id, account_id, debit, credit, description)
                       VALUES (?, ?, ?, ?, ?);""",
                    (entry_id, line["account_id"], line.get("debit", 0),
                     line.get("credit", 0), line.get("description", "")),
                )

        return entry_id, entry_number

    # =================================================================
    # صدور خودکار سند برای فاکتور فروش/خرید و تراکنش خزانه
    # =================================================================
    def auto_post_sale_invoice(self, invoice_id, invoice_number, total_amount,
                                payment_type, user_id, date=None):
        """
        بابت فاکتور فروش:
            بدهکار: صندوق (نقدی) یا حسابهای دریافتنی (نسیه)
            بستانکار: فروش کالا
        اگر نگاشت حساب لازم تعریف نشده باشد، این متد بی‌صدا رد می‌شود (سند صادر نمی‌شود)
        تا از خطای عملیاتی برای فروشگاه‌هایی که هنوز حسابداری را راه‌اندازی نکرده‌اند جلوگیری شود.
        """
        debit_key = "cash" if payment_type == "cash" else "accounts_receivable"
        debit_account = self.get_account_mapping(debit_key)
        credit_account = self.get_account_mapping("sales_revenue")
        if not debit_account or not credit_account:
            return None  # نگاشت حساب هنوز تنظیم نشده؛ صدور خودکار سند رد می‌شود

        lines = [
            {"account_id": debit_account, "debit": total_amount, "credit": 0,
             "description": f"بابت فاکتور فروش {invoice_number}"},
            {"account_id": credit_account, "debit": 0, "credit": total_amount,
             "description": f"بابت فاکتور فروش {invoice_number}"},
        ]
        return self.create_journal_entry(
            f"سند خودکار فاکتور فروش {invoice_number}", lines, user_id,
            source_type="sale", source_id=invoice_id, date=date
        )

    def auto_post_purchase_invoice(self, invoice_id, invoice_number, total_amount,
                                    payment_type, user_id, date=None):
        """
        بابت فاکتور خرید:
            بدهکار: موجودی کالا
            بستانکار: صندوق (نقدی) یا حسابهای پرداختنی (نسیه)
        """
        credit_key = "cash" if payment_type == "cash" else "accounts_payable"
        debit_account = self.get_account_mapping("inventory")
        credit_account = self.get_account_mapping(credit_key)
        if not debit_account or not credit_account:
            return None

        lines = [
            {"account_id": debit_account, "debit": total_amount, "credit": 0,
             "description": f"بابت فاکتور خرید {invoice_number}"},
            {"account_id": credit_account, "debit": 0, "credit": total_amount,
             "description": f"بابت فاکتور خرید {invoice_number}"},
        ]
        return self.create_journal_entry(
            f"سند خودکار فاکتور خرید {invoice_number}", lines, user_id,
            source_type="purchase", source_id=invoice_id, date=date
        )

    def auto_post_treasury_transaction(self, trans_id, trans_type, amount,
                                        user_id, description="", date=None):
        """
        بابت دریافت/پرداخت خزانه:
            دریافت وجه: بدهکار صندوق / بستانکار حسابهای دریافتنی
            پرداخت وجه: بدهکار حسابهای پرداختنی / بستانکار صندوق
        """
        cash_account = self.get_account_mapping("cash")
        other_account = self.get_account_mapping(
            "accounts_receivable" if trans_type == "receive" else "accounts_payable"
        )
        if not cash_account or not other_account:
            return None

        if trans_type == "receive":
            lines = [
                {"account_id": cash_account, "debit": amount, "credit": 0, "description": description},
                {"account_id": other_account, "debit": 0, "credit": amount, "description": description},
            ]
        else:
            lines = [
                {"account_id": other_account, "debit": amount, "credit": 0, "description": description},
                {"account_id": cash_account, "debit": 0, "credit": amount, "description": description},
            ]

        return self.create_journal_entry(
            f"سند خودکار خزانه: {description or trans_type}", lines, user_id,
            source_type="treasury", source_id=trans_id, date=date
        )

    # =================================================================
    # دفتر کل - گردش یک حساب مشخص
    # =================================================================
    def get_general_ledger(self, account_id, date_from=None, date_to=None):
        query = """
            SELECT je.date, je.entry_number, jel.debit, jel.credit, jel.description
            FROM journal_entry_lines jel
            JOIN journal_entries je ON jel.entry_id = je.id
            WHERE jel.account_id = ?
        """
        params = [account_id]
        if date_from:
            query += " AND je.date >= ?"
            params.append(date_from)
        if date_to:
            query += " AND je.date <= ?"
            params.append(date_to)
        query += " ORDER BY je.date, je.id;"

        rows = self.db.fetch_all(query, tuple(params))

        ledger = []
        running_balance = 0
        for row in rows:
            running_balance += row["debit"] - row["credit"]
            ledger.append({
                "date": row["date"],
                "entry_number": row["entry_number"],
                "debit": row["debit"],
                "credit": row["credit"],
                "description": row["description"],
                "balance": running_balance,
            })
        return ledger

    # =================================================================
    # تراز آزمایشی
    # =================================================================
    def get_trial_balance(self, date_from=None, date_to=None):
        query = """
            SELECT a.id, a.code, a.name, a.account_type,
                   COALESCE(SUM(jel.debit), 0) AS total_debit,
                   COALESCE(SUM(jel.credit), 0) AS total_credit
            FROM accounts a
            LEFT JOIN journal_entry_lines jel ON jel.account_id = a.id
            LEFT JOIN journal_entries je ON jel.entry_id = je.id
        """
        conditions = []
        params = []
        if date_from:
            conditions.append("(je.date IS NULL OR je.date >= ?)")
            params.append(date_from)
        if date_to:
            conditions.append("(je.date IS NULL OR je.date <= ?)")
            params.append(date_to)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " GROUP BY a.id ORDER BY a.code;"

        return self.db.fetch_all(query, tuple(params))

    # =================================================================
    # سود و زیان (درآمد - هزینه در یک بازه زمانی)
    # =================================================================
    def get_profit_and_loss(self, date_from, date_to):
        rows = self.get_trial_balance(date_from, date_to)
        total_revenue = sum(r["total_credit"] - r["total_debit"] for r in rows if r["account_type"] == "revenue")
        total_expense = sum(r["total_debit"] - r["total_credit"] for r in rows if r["account_type"] == "expense")
        net_profit = total_revenue - total_expense
        revenue_accounts = [r for r in rows if r["account_type"] == "revenue"]
        expense_accounts = [r for r in rows if r["account_type"] == "expense"]
        return {
            "revenue_accounts": revenue_accounts,
            "expense_accounts": expense_accounts,
            "total_revenue": total_revenue,
            "total_expense": total_expense,
            "net_profit": net_profit,
        }

    # =================================================================
    # ترازنامه (مانده حسابهای دارایی/بدهی/سرمایه تا یک تاریخ)
    # =================================================================
    def get_balance_sheet(self, as_of_date=None):
        rows = self.get_trial_balance(date_to=as_of_date)
        assets = [r for r in rows if r["account_type"] == "asset"]
        liabilities = [r for r in rows if r["account_type"] == "liability"]
        equity = [r for r in rows if r["account_type"] == "equity"]

        total_assets = sum(r["total_debit"] - r["total_credit"] for r in assets)
        total_liabilities = sum(r["total_credit"] - r["total_debit"] for r in liabilities)
        total_equity = sum(r["total_credit"] - r["total_debit"] for r in equity)

        return {
            "assets": assets,
            "liabilities": liabilities,
            "equity": equity,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
        }
