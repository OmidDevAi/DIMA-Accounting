# -*- coding: utf-8 -*-
"""
core/barcode_scanner.py
--------------------------
پشتیبانی از دو نوع دستگاه بارکدخوان:

    ۱. USB با شبیه‌سازی کیبورد (اکثر مدل‌های بازار):
       نیازی به کد یا کتابخانه‌ی اضافه ندارد، چون دستگاه دقیقاً مثل تایپ سریع
       عمل می‌کند؛ همان QLineEdit موجود در فرم فروش/خرید (که با فشردن Enter
       پردازش می‌شود) به‌طور طبیعی این ورودی را می‌گیرد.

    ۲. سریال روی پورت COM (مدل‌های صنعتی/قدیمی‌تر):
       این دستگاه‌ها کیبورد را شبیه‌سازی نمی‌کنند و باید مستقیماً از پورت
       سریال خوانده شوند؛ این کار با کتابخانه‌ی pyserial و در یک QThread
       پس‌زمینه (SerialBarcodeReader) انجام می‌شود تا رابط کاربری هنگام
       انتظار برای اسکن قفل نشود.
"""

from PyQt6.QtCore import QThread, pyqtSignal

try:
    import serial
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False


class SerialBarcodeReader(QThread):
    """
    خواندن پیوسته‌ی بارکد از یک بارکدخوان سریال (COM) در یک ترد پس‌زمینه.
    هر بارکد خوانده‌شده از طریق سیگنال barcode_scanned به بیرون ارسال می‌شود.
    """
    barcode_scanned = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, port, baud_rate=9600, parent=None):
        super().__init__(parent)
        self.port = port
        self.baud_rate = baud_rate
        self._running = False
        self._serial_conn = None

    def run(self):
        if not PYSERIAL_AVAILABLE:
            self.error_occurred.emit(
                "کتابخانه pyserial نصب نیست. برای استفاده از بارکدخوان سریال، "
                "دستور 'pip install pyserial' را اجرا کنید."
            )
            return
        try:
            self._serial_conn = serial.Serial(self.port, self.baud_rate, timeout=1)
        except Exception as e:
            self.error_occurred.emit(f"اتصال به پورت {self.port} ناموفق بود: {e}")
            return

        self._running = True
        while self._running:
            try:
                raw = self._serial_conn.readline()
                if not raw:
                    continue
                text = raw.decode("utf-8", errors="ignore").strip()
                if text:
                    self.barcode_scanned.emit(text)
            except Exception as e:
                self.error_occurred.emit(f"خطا در خواندن از بارکدخوان سریال: {e}")
                break

        if self._serial_conn:
            self._serial_conn.close()

    def stop(self):
        """توقف ایمن ترد؛ باید هنگام بستن برنامه یا صفحه فراخوانی شود."""
        self._running = False
        self.wait(2000)
