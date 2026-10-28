# -*- coding: utf-8 -*-
"""
modules/sms_providers.py
---------------------------
لایه‌ی انتزاعی سرویس‌دهنده‌ی پیامک.

هدف معماری این فایل: وقتی فروشگاه سرویس‌دهنده‌ی پیامک خودش را عوض کرد (مثلاً
از کاوه‌نگار به ملی‌پیامک، یا به یک سرویس‌دهنده‌ی کاملاً جدید که هنوز وجود
ندارد)، هیچ تغییری در بقیه‌ی نرم‌افزار (فرم فروش، صفحه‌ی مشتریان و ...) لازم
نباشد؛ فقط کافی است در صفحه‌ی «تنظیمات → پیامک»، سرویس‌دهنده و مقادیرش عوض شود.

سه گزینه فراهم شده:
    ۱. KavenegarProvider   - پیاده‌سازی آماده برای کاوه‌نگار
    ۲. MelipayamakProvider - پیاده‌سازی آماده برای ملی‌پیامک
    ۳. GenericHTTPProvider - برای هر سرویس‌دهنده‌ی دیگری (حتی آینده)؛ آدرس،
       روش HTTP، و قالب بدنه‌ی پیام کاملاً از تنظیمات خوانده می‌شود.

⚠️ نکته مهم: پیاده‌سازی کاوه‌نگار و ملی‌پیامک بر اساس مستندات عمومی این
سرویس‌دهنده‌ها نوشته شده است. چون مستندات API شرکت‌های ثالث ممکن است در طول
زمان تغییر کند، حتماً قبل از اتصال واقعی، آدرس/پارامترها را با آخرین نسخه‌ی
مستندات رسمی همان سرویس‌دهنده مطابقت دهید.
"""

import json

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class SMSProviderBase:
    """رابط پایه؛ هر سرویس‌دهنده‌ی جدید باید از این کلاس ارث‌بری کند."""

    def send(self, phone: str, message: str, settings: dict) -> dict:
        """
        بازگشت: {"success": bool, "status": str, "response_snippet": str}
        """
        raise NotImplementedError


class KavenegarProvider(SMSProviderBase):
    """سرویس‌دهنده‌ی کاوه‌نگار (api.kavenegar.com)."""

    def send(self, phone, message, settings):
        if not REQUESTS_AVAILABLE:
            return {"success": False, "status": "requests_not_installed", "response_snippet": ""}

        api_key = settings.get("api_key", "")
        if not api_key:
            return {"success": False, "status": "not_configured", "response_snippet": ""}

        url = f"https://api.kavenegar.com/v1/{api_key}/sms/send.json"
        params = {"receptor": phone, "message": message}
        sender = settings.get("sender_number", "")
        if sender:
            params["sender"] = sender

        try:
            resp = requests.get(url, params=params, timeout=10)
            success = resp.status_code == 200
            return {
                "success": success,
                "status": "sent" if success else "failed",
                "response_snippet": resp.text[:300],
            }
        except Exception as e:
            return {"success": False, "status": "error", "response_snippet": str(e)[:300]}


class MelipayamakProvider(SMSProviderBase):
    """
    سرویس‌دهنده‌ی ملی‌پیامک (rest.payamak-panel.com).
    توجه: این سرویس‌دهنده معمولاً به‌جای یک API Key ساده، از نام‌کاربری/رمز
    پنل استفاده می‌کند. نام‌کاربری را در فیلد «API Key» و رمز عبور را در
    فیلد «آدرس API» (به‌صورت موقت) در تنظیمات وارد کنید، یا این کلاس را
    مطابق روش احراز هویت واقعی حساب خودتان اصلاح کنید.
    """

    def send(self, phone, message, settings):
        if not REQUESTS_AVAILABLE:
            return {"success": False, "status": "requests_not_installed", "response_snippet": ""}

        username = settings.get("api_key", "")
        password = settings.get("api_url", "")
        if not username or not password:
            return {"success": False, "status": "not_configured", "response_snippet": ""}

        url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"
        payload = {
            "username": username,
            "password": password,
            "to": phone,
            "from": settings.get("sender_number", ""),
            "text": message,
            "isflash": False,
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            success = resp.status_code == 200
            return {
                "success": success,
                "status": "sent" if success else "failed",
                "response_snippet": resp.text[:300],
            }
        except Exception as e:
            return {"success": False, "status": "error", "response_snippet": str(e)[:300]}


class GenericHTTPProvider(SMSProviderBase):
    """
    برای هر سرویس‌دهنده‌ی دیگری (فعلی یا آینده) که آداپتور اختصاصی ندارد.
    آدرس API، روش HTTP، و قالب بدنه‌ی پیام (Payload Template) کاملاً از
    تنظیمات خوانده می‌شود؛ یعنی برای تعویض سرویس‌دهنده در آینده، کافی است
    این مقادیر در صفحه‌ی تنظیمات به‌روزرسانی شوند - نیازی به تغییر کد نیست.

    قالب پیام نمونه (JSON، جای‌گزین‌های مجاز: {phone} {message} {sender} {api_key}):
        {"to": "{phone}", "text": "{message}", "from": "{sender}", "key": "{api_key}"}
    """

    DEFAULT_TEMPLATE = '{"to": "{phone}", "text": "{message}", "from": "{sender}", "key": "{api_key}"}'

    @staticmethod
    def _json_escaped_value(value: str) -> str:
        """
        تبدیل یک رشته به محتوای داخلِ escape‌شده‌ی JSON (بدون گیومه‌های اطراف)،
        تا بتوان آن را داخل قالب جای‌گذاری کرد بدون خراب کردن ساختار JSON
        (مثلاً اگر پیام حاوی گیومه یا خط جدید باشد).
        """
        import json as _json
        return _json.dumps(value or "")[1:-1]

    def send(self, phone, message, settings):
        if not REQUESTS_AVAILABLE:
            return {"success": False, "status": "requests_not_installed", "response_snippet": ""}

        api_url = settings.get("api_url", "")
        if not api_url:
            return {"success": False, "status": "not_configured", "response_snippet": "آدرس API تنظیم نشده"}

        template = settings.get("payload_template") or self.DEFAULT_TEMPLATE

        # نکته مهم: از str.format() استفاده نمی‌کنیم چون آکولادهای خودِ JSON
        # (مثل «{» ابتدای شیء) با جای‌گزین‌های {phone}/{message} تداخل پیدا
        # می‌کنند؛ به‌جای آن هر جای‌گزین را جداگانه با محتوای escape‌شده‌ی JSON
        # جایگزین می‌کنیم تا هم تداخل رفع شود و هم کاراکترهای خاص (گیومه و...)
        # ساختار JSON را خراب نکنند.
        rendered = template
        for key, value in (
            ("phone", phone),
            ("message", message),
            ("sender", settings.get("sender_number", "")),
            ("api_key", settings.get("api_key", "")),
        ):
            rendered = rendered.replace("{" + key + "}", self._json_escaped_value(value))

        try:
            payload = json.loads(rendered)
        except (json.JSONDecodeError, ValueError) as e:
            return {"success": False, "status": "invalid_template", "response_snippet": str(e)[:300]}

        method = (settings.get("http_method") or "POST").upper()
        try:
            if method == "GET":
                resp = requests.get(api_url, params=payload, timeout=10)
            else:
                resp = requests.post(api_url, json=payload, timeout=10)
            success = resp.status_code == 200
            return {
                "success": success,
                "status": "sent" if success else "failed",
                "response_snippet": resp.text[:300],
            }
        except Exception as e:
            return {"success": False, "status": "error", "response_snippet": str(e)[:300]}


# نگاشت کلید سرویس‌دهنده (ذخیره‌شده در دیتابیس) به کلاس متناظرش.
# افزودن سرویس‌دهنده‌ی جدید فقط نیازمند یک کلاس جدید و یک خط در همین دیکشنری است.
PROVIDERS = {
    "kavenegar": KavenegarProvider,
    "melipayamak": MelipayamakProvider,
    "generic": GenericHTTPProvider,
}


def get_provider(provider_key: str) -> SMSProviderBase:
    provider_class = PROVIDERS.get(provider_key, GenericHTTPProvider)
    return provider_class()
