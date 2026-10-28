# -*- coding: utf-8 -*-
"""
core/i18n.py
--------------
زیرساخت چندزبانه‌ی برنامه (فارسی، انگلیسی، فرانسه، آلمانی).

روش کار: به‌جای فایل‌های .ts/.qm رسمی Qt (که نیاز به کامپایل جداگانه دارند)،
از یک دیکشنری ساده‌ی کلید→ترجمه استفاده شده تا افزودن رشته‌های جدید سریع و
بدون ابزار جانبی ممکن باشد. هر رشته‌ی قابل‌مشاهده در UI باید به‌جای نوشتن
مستقیم متن فارسی، از طریق تابع tr("کلید") خوانده شود.

⚠️ نکته مهم درباره‌ی حجم کار باقی‌مانده:
    این فایل، خودِ سازوکار ترجمه (زیرساخت) را کامل و آماده می‌کند و صفحات
    اصلی (ورود، سایدبار/پنجره اصلی، داشبورد) را کامل به هر ۴ زبان ترجمه کرده
    است. اما باقی صفحات (فروش، خرید، انبار، حسابداری، مشتریان، چک، تنظیمات و...)
    هنوز رشته‌های فارسی مستقیم دارند و باید هرکدام به‌مرور با همین الگو
    (جایگزینی متن مستقیم با tr("کلید") و افزودن ترجمه‌ی هر ۴ زبان در
    TRANSLATIONS) به‌روزرسانی شوند؛ این کار مکانیکی ولی زمان‌بر است چون
    ده‌ها فایل و صدها رشته‌ی متنی در کل پروژه وجود دارد.
"""

# کد زبان فعلی برنامه؛ توسط LanguageManager در زمان اجرا تغییر می‌کند.
_current_language = "fa"

# زبان‌های پشتیبانی‌شده و اطلاعات نمایشی‌شان.
# "direction" با رشته‌ی ساده ("rtl"/"ltr") ذخیره می‌شود تا این فایل به PyQt6
# وابسته نباشد و بدون رابط کاربری هم قابل تست باشد؛ لایه‌ی UI با
# get_layout_direction() آن را به Qt.LayoutDirection تبدیل می‌کند.
SUPPORTED_LANGUAGES = {
    "fa": {"label": "فارسی", "direction": "rtl"},
    "en": {"label": "English", "direction": "ltr"},
    "fr": {"label": "Français", "direction": "ltr"},
    "de": {"label": "Deutsch", "direction": "ltr"},
}

# دیکشنری ترجمه: {کلید: {کد زبان: متن}}
# کلیدها معنادار و بر اساس محل استفاده نام‌گذاری شده‌اند تا افزودن/جستجوی
# رشته‌ی جدید ساده باشد.
TRANSLATIONS = {
    # ---------------- عمومی/برند ----------------
    "app_title": {
        "fa": "سیستم حسابداری DIMA", "en": "DIMA Accounting System",
        "fr": "Système Comptable DIMA", "de": "DIMA Buchhaltungssystem",
    },
    "brand": {"fa": "دیما", "en": "DIMA", "fr": "DIMA", "de": "DIMA"},

    # ---------------- پنجره ورود ----------------
    "login_subtitle": {
        "fa": "نرم‌افزار یکپارچه فروش، خرید و انبارداری",
        "en": "Integrated Sales, Purchase & Inventory Software",
        "fr": "Logiciel intégré de vente, achat et inventaire",
        "de": "Integrierte Software für Verkauf, Einkauf und Lager",
    },
    "login_username_label": {"fa": "نام کاربری:", "en": "Username:", "fr": "Nom d'utilisateur :", "de": "Benutzername:"},
    "login_username_placeholder": {
        "fa": "نام کاربری خود را وارد کنید", "en": "Enter your username",
        "fr": "Entrez votre nom d'utilisateur", "de": "Benutzernamen eingeben",
    },
    "login_password_label": {"fa": "رمز عبور:", "en": "Password:", "fr": "Mot de passe :", "de": "Passwort:"},
    "login_password_placeholder": {"fa": "رمز عبور", "en": "Password", "fr": "Mot de passe", "de": "Passwort"},
    "login_button": {"fa": "ورود به سیستم", "en": "Sign In", "fr": "Se connecter", "de": "Anmelden"},
    "login_error_empty": {
        "fa": "لطفاً نام کاربری و رمز عبور را وارد کنید.",
        "en": "Please enter your username and password.",
        "fr": "Veuillez saisir votre nom d'utilisateur et mot de passe.",
        "de": "Bitte Benutzername und Passwort eingeben.",
    },
    "login_error_invalid": {
        "fa": "نام کاربری یا رمز عبور اشتباه است.",
        "en": "Incorrect username or password.",
        "fr": "Nom d'utilisateur ou mot de passe incorrect.",
        "de": "Benutzername oder Passwort falsch.",
    },
    "login_hint": {
        "fa": "کاربر پیش‌فرض: admin / رمز: admin123",
        "en": "Default user: admin / password: admin123",
        "fr": "Utilisateur par défaut : admin / mot de passe : admin123",
        "de": "Standardbenutzer: admin / Passwort: admin123",
    },

    # ---------------- سایدبار / پنجره اصلی ----------------
    "menu_dashboard": {"fa": "داشبورد", "en": "Dashboard", "fr": "Tableau de bord", "de": "Übersicht"},
    "menu_sales": {"fa": "فروش سریع", "en": "Quick Sale", "fr": "Vente rapide", "de": "Schnellverkauf"},
    "menu_purchase": {"fa": "فاکتور خرید", "en": "Purchase Invoice", "fr": "Facture d'achat", "de": "Einkaufsrechnung"},
    "menu_inventory": {"fa": "انبار و کالا", "en": "Inventory", "fr": "Inventaire", "de": "Lager & Artikel"},
    "menu_customers": {"fa": "مشتریان", "en": "Customers", "fr": "Clients", "de": "Kunden"},
    "menu_invoices": {"fa": "تاریخچه فاکتورها", "en": "Invoice History", "fr": "Historique des factures", "de": "Rechnungsverlauf"},
    "menu_treasury": {"fa": "خزانه‌داری", "en": "Treasury", "fr": "Trésorerie", "de": "Kasse"},
    "menu_checks": {"fa": "چک‌ها", "en": "Checks", "fr": "Chèques", "de": "Schecks"},
    "menu_accounting": {"fa": "حسابداری", "en": "Accounting", "fr": "Comptabilité", "de": "Buchhaltung"},
    "menu_settings": {"fa": "تنظیمات", "en": "Settings", "fr": "Paramètres", "de": "Einstellungen"},
    "menu_logout": {"fa": "خروج از حساب", "en": "Log Out", "fr": "Déconnexion", "de": "Abmelden"},
    "language_label": {"fa": "زبان:", "en": "Language:", "fr": "Langue :", "de": "Sprache:"},

    "role_admin": {"fa": "مدیر فروشگاه", "en": "Store Manager", "fr": "Gérant du magasin", "de": "Filialleiter"},
    "role_accountant": {"fa": "حسابدار", "en": "Accountant", "fr": "Comptable", "de": "Buchhalter"},
    "role_cashier": {"fa": "صندوق‌دار", "en": "Cashier", "fr": "Caissier", "de": "Kassierer"},
    "status_bar_user": {
        "fa": "کاربر جاری: {name} | نقش: {role}",
        "en": "Current user: {name} | Role: {role}",
        "fr": "Utilisateur actuel : {name} | Rôle : {role}",
        "de": "Aktueller Benutzer: {name} | Rolle: {role}",
    },

    # ---------------- داشبورد ----------------
    "dashboard_welcome": {
        "fa": "خوش آمدید، {name}", "en": "Welcome, {name}",
        "fr": "Bienvenue, {name}", "de": "Willkommen, {name}",
    },
    "dashboard_sales_count": {
        "fa": "تعداد فاکتورهای فروش", "en": "Number of Sales Invoices",
        "fr": "Nombre de factures de vente", "de": "Anzahl Verkaufsrechnungen",
    },
    "dashboard_low_stock": {
        "fa": "کالاهای زیر نقطه سفارش", "en": "Items Below Reorder Point",
        "fr": "Articles sous le seuil de commande", "de": "Artikel unter Meldebestand",
    },
    "dashboard_box_balance": {
        "fa": "مانده صندوق فعال", "en": "Active Register Balance",
        "fr": "Solde de caisse actif", "de": "Aktueller Kassenstand",
    },
    "dashboard_all_boxes": {"fa": "همه صندوق‌ها", "en": "All Registers", "fr": "Toutes les caisses", "de": "Alle Kassen"},

    # ---------------- فاکتور فروش سریع ----------------
    "sales_page_title": {"fa": "فروش سریع", "en": "Quick Sale", "fr": "Vente rapide", "de": "Schnellverkauf"},
    "sales_new_invoice_btn": {
        "fa": "+ فاکتور جدید (مشتری بعدی)", "en": "+ New Invoice (Next Customer)",
        "fr": "+ Nouvelle facture (client suivant)", "de": "+ Neue Rechnung (Nächster Kunde)",
    },
    "sales_tab_name": {"fa": "فاکتور {n}", "en": "Invoice {n}", "fr": "Facture {n}", "de": "Rechnung {n}"},
    "sales_scan_barcode_label": {"fa": "اسکن بارکد:", "en": "Scan Barcode:", "fr": "Scanner le code-barres :", "de": "Barcode scannen:"},
    "sales_scan_barcode_placeholder": {
        "fa": "بارکد کالا را اسکن کنید یا وارد نمایید و Enter بزنید...",
        "en": "Scan or enter the product barcode and press Enter...",
        "fr": "Scannez ou saisissez le code-barres et appuyez sur Entrée...",
        "de": "Barcode scannen oder eingeben und Enter drücken...",
    },
    "sales_customer_phone_label": {"fa": "موبایل مشتری:", "en": "Customer Mobile:", "fr": "Mobile du client :", "de": "Kundenhandy:"},
    "sales_customer_phone_placeholder": {
        "fa": "شماره موبایل مشتری (اختیاری)", "en": "Customer mobile number (optional)",
        "fr": "Numéro de mobile du client (facultatif)", "de": "Kundenhandynummer (optional)",
    },
    "sales_customer_name_placeholder": {
        "fa": "نام مشتری (فقط اگر مشتری جدید است)", "en": "Customer name (only if new customer)",
        "fr": "Nom du client (seulement si nouveau client)", "de": "Kundenname (nur bei Neukunde)",
    },
    "sales_wholesale_checkbox": {"fa": "فاکتور عمده (F11)", "en": "Wholesale Invoice (F11)", "fr": "Facture de gros (F11)", "de": "Großhandelsrechnung (F11)"},
    "sales_col_product_id": {"fa": "شناسه کالا", "en": "Product ID", "fr": "ID produit", "de": "Artikel-ID"},
    "sales_col_product_name": {"fa": "نام کالا", "en": "Product Name", "fr": "Nom du produit", "de": "Artikelname"},
    "sales_col_qty": {"fa": "تعداد", "en": "Qty", "fr": "Quantité", "de": "Menge"},
    "sales_col_price_tier": {"fa": "سطح قیمت", "en": "Price Tier", "fr": "Niveau de prix", "de": "Preisstufe"},
    "sales_col_unit_price": {"fa": "قیمت واحد", "en": "Unit Price", "fr": "Prix unitaire", "de": "Einzelpreis"},
    "sales_col_line_total": {"fa": "جمع", "en": "Total", "fr": "Total", "de": "Summe"},
    "sales_invoice_discount_label": {"fa": "تخفیف کل فاکتور:", "en": "Total Invoice Discount:", "fr": "Remise totale sur facture :", "de": "Gesamtrabatt der Rechnung:"},
    "discount_type_rial": {"fa": "ریال", "en": "Amount", "fr": "Montant", "de": "Betrag"},
    "discount_type_percent": {"fa": "درصد", "en": "Percent", "fr": "Pourcentage", "de": "Prozent"},
    "sales_payment_type_label": {"fa": "نوع پرداخت:", "en": "Payment Type:", "fr": "Mode de paiement :", "de": "Zahlungsart:"},
    "payment_cash": {"fa": "نقدی (F2)", "en": "Cash (F2)", "fr": "Espèces (F2)", "de": "Bar (F2)"},
    "payment_credit": {"fa": "نسیه", "en": "Credit", "fr": "Crédit", "de": "Kredit"},
    "payment_card": {"fa": "کارتی (F6)", "en": "Card (F6)", "fr": "Carte (F6)", "de": "Karte (F6)"},
    "sales_total_label": {"fa": "جمع کل: {amount} ریال", "en": "Total: {amount}", "fr": "Total : {amount}", "de": "Summe: {amount}"},
    "sales_submit_btn": {"fa": "ثبت فاکتور (F2)", "en": "Submit Invoice (F2)", "fr": "Valider la facture (F2)", "de": "Rechnung buchen (F2)"},
    "remove_btn": {"fa": "حذف", "en": "Remove", "fr": "Supprimer", "de": "Entfernen"},
    "sales_empty_cart": {"fa": "سبد فروش خالی است.", "en": "The cart is empty.", "fr": "Le panier est vide.", "de": "Der Warenkorb ist leer."},
    "sales_no_active_box": {
        "fa": "کاربر ادمین باید یک صندوق فعال برای ثبت فاکتور انتخاب کند.",
        "en": "Admin must select an active register to submit an invoice.",
        "fr": "L'administrateur doit sélectionner une caisse active pour valider la facture.",
        "de": "Der Administrator muss eine aktive Kasse zum Buchen auswählen.",
    },
    "sales_success_title": {"fa": "موفق", "en": "Success", "fr": "Succès", "de": "Erfolg"},
    "sales_success_message": {
        "fa": "فاکتور شماره {number} با مبلغ {amount} ریال با موفقیت ثبت شد.",
        "en": "Invoice {number} for {amount} was submitted successfully.",
        "fr": "La facture {number} d'un montant de {amount} a été enregistrée avec succès.",
        "de": "Rechnung {number} über {amount} wurde erfolgreich gebucht.",
    },
    "sales_invoice_sale_label": {"fa": "فاکتور فروش", "en": "Sales Invoice", "fr": "Facture de vente", "de": "Verkaufsrechnung"},
    "warning_title": {"fa": "خطا", "en": "Error", "fr": "Erreur", "de": "Fehler"},
    "info_title": {"fa": "توجه", "en": "Notice", "fr": "Avis", "de": "Hinweis"},
    "sales_not_found_title": {"fa": "یافت نشد", "en": "Not Found", "fr": "Introuvable", "de": "Nicht gefunden"},
    "sales_not_found_message": {
        "fa": "کالایی با بارکد «{barcode}» یافت نشد.",
        "en": "No product found with barcode \"{barcode}\".",
        "fr": "Aucun produit trouvé avec le code-barres « {barcode} ».",
        "de": "Kein Artikel mit Barcode „{barcode}“ gefunden.",
    },
    "sales_stock_error_title": {"fa": "موجودی ناکافی", "en": "Insufficient Stock", "fr": "Stock insuffisant", "de": "Unzureichender Bestand"},
    "sales_new_customer_title": {"fa": "مشتری جدید", "en": "New Customer", "fr": "Nouveau client", "de": "Neuer Kunde"},
    "sales_new_customer_prompt": {
        "fa": "مشتری‌ای با شماره «{phone}» قبلاً ثبت نشده.\nنام مشتری را وارد کنید:",
        "en": "No customer registered with number \"{phone}\" yet.\nEnter the customer's name:",
        "fr": "Aucun client enregistré avec le numéro « {phone} ».\nEntrez le nom du client :",
        "de": "Noch kein Kunde mit der Nummer „{phone}“ registriert.\nName des Kunden eingeben:",
    },

    # ---------------- فاکتور خرید پیشرفته ----------------
    "purchase_page_title": {"fa": "فاکتور خرید پیشرفته", "en": "Advanced Purchase Invoice", "fr": "Facture d'achat avancée", "de": "Erweiterte Einkaufsrechnung"},
    "purchase_supplier_label": {"fa": "تامین‌کننده:", "en": "Supplier:", "fr": "Fournisseur :", "de": "Lieferant:"},
    "purchase_no_supplier": {"fa": "بدون تامین‌کننده", "en": "No Supplier", "fr": "Sans fournisseur", "de": "Ohne Lieferant"},
    "purchase_payment_label": {"fa": "نوع پرداخت:", "en": "Payment Type:", "fr": "Mode de paiement :", "de": "Zahlungsart:"},
    "purchase_add_item_btn": {"fa": "+ افزودن کالا", "en": "+ Add Item", "fr": "+ Ajouter un article", "de": "+ Artikel hinzufügen"},
    "purchase_col_barcode": {"fa": "بارکد", "en": "Barcode", "fr": "Code-barres", "de": "Barcode"},
    "purchase_col_code": {"fa": "کد کالا", "en": "Product Code", "fr": "Code produit", "de": "Artikelcode"},
    "purchase_col_name": {"fa": "نام محصول", "en": "Product Name", "fr": "Nom du produit", "de": "Artikelname"},
    "purchase_col_qty_num": {"fa": "تعداد عددی", "en": "Unit Qty", "fr": "Qté unité", "de": "Stückzahl"},
    "purchase_col_qty_box": {"fa": "تعداد جعبه", "en": "Box Qty", "fr": "Qté boîte", "de": "Kartonmenge"},
    "purchase_col_gift": {"fa": "هدیه", "en": "Gift", "fr": "Cadeau", "de": "Geschenk"},
    "purchase_col_buy_price": {"fa": "قیمت خرید", "en": "Buy Price", "fr": "Prix d'achat", "de": "Einkaufspreis"},
    "purchase_col_discount": {"fa": "تخفیف", "en": "Discount", "fr": "Remise", "de": "Rabatt"},
    "purchase_col_tax": {"fa": "مالیات", "en": "Tax", "fr": "Taxe", "de": "Steuer"},
    "purchase_col_line_total": {"fa": "جمع سطر", "en": "Line Total", "fr": "Total ligne", "de": "Zeilensumme"},
    "purchase_invoice_discount_label": {"fa": "تخفیف کل فاکتور:", "en": "Total Invoice Discount:", "fr": "Remise totale sur facture :", "de": "Gesamtrabatt der Rechnung:"},
    "purchase_duty_label": {"fa": "عوارض کل فاکتور:", "en": "Total Invoice Duty:", "fr": "Taxe totale sur facture :", "de": "Gesamtabgabe der Rechnung:"},
    "purchase_total_label": {"fa": "جمع کل فاکتور: {amount} ریال", "en": "Invoice Total: {amount}", "fr": "Total de la facture : {amount}", "de": "Rechnungssumme: {amount}"},
    "purchase_submit_btn": {"fa": "ثبت فاکتور خرید", "en": "Submit Purchase Invoice", "fr": "Valider la facture d'achat", "de": "Einkaufsrechnung buchen"},
    "purchase_empty_items": {
        "fa": "حداقل یک کالا باید به فاکتور اضافه شود.", "en": "At least one item must be added to the invoice.",
        "fr": "Au moins un article doit être ajouté à la facture.", "de": "Mindestens ein Artikel muss der Rechnung hinzugefügt werden.",
    },
    "purchase_no_active_box": {
        "fa": "کاربر ادمین باید یک صندوق فعال برای ثبت فاکتور انتخاب کند.",
        "en": "Admin must select an active register to submit an invoice.",
        "fr": "L'administrateur doit sélectionner une caisse active pour valider la facture.",
        "de": "Der Administrator muss eine aktive Kasse zum Buchen auswählen.",
    },
    "purchase_success_message": {
        "fa": "فاکتور خرید شماره {number} با مبلغ {amount} ریال ثبت شد.",
        "en": "Purchase invoice {number} for {amount} was submitted.",
        "fr": "La facture d'achat {number} d'un montant de {amount} a été enregistrée.",
        "de": "Einkaufsrechnung {number} über {amount} wurde gebucht.",
    },
    "purchase_error_submit": {
        "fa": "خطا در ثبت فاکتور خرید:\n{error}", "en": "Error submitting purchase invoice:\n{error}",
        "fr": "Erreur lors de la validation de la facture d'achat :\n{error}", "de": "Fehler beim Buchen der Einkaufsrechnung:\n{error}",
    },
    "purchase_invoice_label": {"fa": "فاکتور خرید", "en": "Purchase Invoice", "fr": "Facture d'achat", "de": "Einkaufsrechnung"},

    # ---------------- فرم افزودن کالا (خرید) ----------------
    "purchase_item_dialog_title": {"fa": "افزودن کالا به فاکتور خرید", "en": "Add Item to Purchase Invoice", "fr": "Ajouter un article à la facture d'achat", "de": "Artikel zur Einkaufsrechnung hinzufügen"},
    "purchase_item_search_label": {"fa": "بارکد / کد کالا:", "en": "Barcode / Product Code:", "fr": "Code-barres / Code produit :", "de": "Barcode / Artikelcode:"},
    "purchase_item_search_placeholder": {
        "fa": "بارکد یا کد کالا را وارد کنید...", "en": "Enter the barcode or product code...",
        "fr": "Entrez le code-barres ou le code produit...", "de": "Barcode oder Artikelcode eingeben...",
    },
    "search_btn": {"fa": "جستجو", "en": "Search", "fr": "Rechercher", "de": "Suchen"},
    "purchase_item_name_label": {"fa": "نام کالا:", "en": "Product Name:", "fr": "Nom du produit :", "de": "Artikelname:"},
    "purchase_item_no_selection": {"fa": "— کالایی انتخاب نشده —", "en": "— No item selected —", "fr": "— Aucun article sélectionné —", "de": "— Kein Artikel ausgewählt —"},
    "purchase_item_qty_num_label": {"fa": "تعداد عددی:", "en": "Unit Quantity:", "fr": "Quantité unité :", "de": "Stückzahl:"},
    "purchase_item_qty_box_label": {"fa": "تعداد جعبه:", "en": "Box Quantity:", "fr": "Quantité boîte :", "de": "Kartonmenge:"},
    "purchase_item_gift_label": {"fa": "مقدار هدیه:", "en": "Gift Quantity:", "fr": "Quantité cadeau :", "de": "Geschenkmenge:"},
    "purchase_item_price_label": {"fa": "قیمت خرید (واحد):", "en": "Buy Price (Unit):", "fr": "Prix d'achat (unité) :", "de": "Einkaufspreis (Einheit):"},
    "purchase_item_discount_label": {"fa": "تخفیف ردیف:", "en": "Line Discount:", "fr": "Remise ligne :", "de": "Zeilenrabatt:"},
    "purchase_item_tax_label": {"fa": "مالیات:", "en": "Tax:", "fr": "Taxe :", "de": "Steuer:"},
    "purchase_item_has_tax_checkbox": {"fa": "این کالا مالیات دارد", "en": "This item has tax", "fr": "Cet article est taxé", "de": "Dieser Artikel hat Steuer"},
    "purchase_item_percent_label": {"fa": "درصد:", "en": "Percent:", "fr": "Pourcentage :", "de": "Prozent:"},
    "purchase_item_prod_date_label": {"fa": "تاریخ تولید:", "en": "Production Date:", "fr": "Date de production :", "de": "Herstellungsdatum:"},
    "purchase_item_exp_date_label": {"fa": "تاریخ انقضا:", "en": "Expiry Date:", "fr": "Date d'expiration :", "de": "Verfallsdatum:"},
    "purchase_item_add_btn": {"fa": "افزودن به فاکتور", "en": "Add to Invoice", "fr": "Ajouter à la facture", "de": "Zur Rechnung hinzufügen"},
    "purchase_item_not_found_title": {"fa": "یافت نشد", "en": "Not Found", "fr": "Introuvable", "de": "Nicht gefunden"},
    "purchase_item_not_found_message": {
        "fa": "کالایی با این بارکد/کد یافت نشد.", "en": "No item found with this barcode/code.",
        "fr": "Aucun article trouvé avec ce code-barres/code.", "de": "Kein Artikel mit diesem Barcode/Code gefunden.",
    },
    "purchase_item_error_no_product": {
        "fa": "ابتدا باید یک کالای معتبر جستجو/انتخاب کنید.", "en": "You must search/select a valid item first.",
        "fr": "Vous devez d'abord rechercher/sélectionner un article valide.", "de": "Zuerst muss ein gültiger Artikel gesucht/ausgewählt werden.",
    },
    "purchase_item_error_no_qty": {
        "fa": "حداقل یکی از تعداد عددی یا تعداد جعبه باید بزرگ‌تر از صفر باشد.",
        "en": "At least one of unit quantity or box quantity must be greater than zero.",
        "fr": "Au moins une des quantités (unité ou boîte) doit être supérieure à zéro.",
        "de": "Mindestens Stückzahl oder Kartonmenge muss größer als null sein.",
    },
    "purchase_item_error_no_price": {
        "fa": "قیمت خرید را وارد کنید (چون همیشه در حال تغییر است، خودکار پر نمی‌شود).",
        "en": "Enter the buy price (it is never auto-filled since prices change constantly).",
        "fr": "Saisissez le prix d'achat (il n'est jamais prérempli car les prix changent constamment).",
        "de": "Einkaufspreis eingeben (wird nie automatisch ausgefüllt, da sich Preise ständig ändern).",
    },

    # ---------------- انبار و کالا ----------------
    "inventory_page_title": {"fa": "مدیریت کالا و انبار", "en": "Inventory & Product Management", "fr": "Gestion des stocks et produits", "de": "Lager- & Artikelverwaltung"},
    "inventory_access_denied": {
        "fa": "دسترسی به مدیریت کالا و قیمت‌ها فقط برای مدیر فروشگاه و حسابدار مجاز است.",
        "en": "Access to product and price management is only allowed for the store manager and accountant.",
        "fr": "L'accès à la gestion des produits et des prix est réservé au gérant et au comptable.",
        "de": "Der Zugriff auf Artikel- und Preisverwaltung ist nur dem Filialleiter und Buchhalter erlaubt.",
    },
    "inventory_search_placeholder": {
        "fa": "جستجو بر اساس نام، کد یا بارکد...", "en": "Search by name, code, or barcode...",
        "fr": "Rechercher par nom, code ou code-barres...", "de": "Suche nach Name, Code oder Barcode...",
    },
    "inventory_add_product_btn": {"fa": "+ افزودن کالای جدید", "en": "+ Add New Item", "fr": "+ Ajouter un nouvel article", "de": "+ Neuen Artikel hinzufügen"},
    "edit_btn": {"fa": "ویرایش", "en": "Edit", "fr": "Modifier", "de": "Bearbeiten"},
    "delete_btn": {"fa": "حذف", "en": "Delete", "fr": "Supprimer", "de": "Löschen"},
    "inventory_add_group_btn": {"fa": "+ گروه/زیرگروه جدید", "en": "+ New Group/Subgroup", "fr": "+ Nouveau groupe/sous-groupe", "de": "+ Neue Gruppe/Untergruppe"},
    "inventory_edit_labels_btn": {"fa": "ویرایش عناوین قیمت‌ها", "en": "Edit Price Labels", "fr": "Modifier les libellés de prix", "de": "Preisbezeichnungen bearbeiten"},
    "inventory_col_id": {"fa": "شناسه", "en": "ID", "fr": "ID", "de": "ID"},
    "inventory_col_barcode": {"fa": "بارکد", "en": "Barcode", "fr": "Code-barres", "de": "Barcode"},
    "inventory_col_code": {"fa": "کد", "en": "Code", "fr": "Code", "de": "Code"},
    "inventory_col_name": {"fa": "نام کالا", "en": "Item Name", "fr": "Nom de l'article", "de": "Artikelname"},
    "inventory_col_stock": {"fa": "موجودی", "en": "Stock", "fr": "Stock", "de": "Bestand"},
    "inventory_select_first": {"fa": "لطفاً ابتدا یک کالا را انتخاب کنید.", "en": "Please select an item first.", "fr": "Veuillez d'abord sélectionner un article.", "de": "Bitte zuerst einen Artikel auswählen."},
    "inventory_error_code_name_required": {
        "fa": "کد و نام کالا الزامی است.", "en": "Item code and name are required.",
        "fr": "Le code et le nom de l'article sont obligatoires.", "de": "Artikelcode und -name sind erforderlich.",
    },
    "inventory_error_save": {"fa": "خطا در ذخیره کالا:\n{error}", "en": "Error saving item:\n{error}", "fr": "Erreur lors de l'enregistrement de l'article :\n{error}", "de": "Fehler beim Speichern des Artikels:\n{error}"},
    "inventory_confirm_delete_title": {"fa": "تایید حذف", "en": "Confirm Delete", "fr": "Confirmer la suppression", "de": "Löschen bestätigen"},
    "inventory_confirm_delete_message": {"fa": "آیا از حذف این کالا اطمینان دارید؟", "en": "Are you sure you want to delete this item?", "fr": "Voulez-vous vraiment supprimer cet article ?", "de": "Möchten Sie diesen Artikel wirklich löschen?"},
    "inventory_error_delete": {
        "fa": "امکان حذف وجود ندارد (احتمالاً در فاکتوری استفاده شده است):\n{error}",
        "en": "Cannot delete (it is probably used in an invoice):\n{error}",
        "fr": "Suppression impossible (probablement utilisé dans une facture) :\n{error}",
        "de": "Löschen nicht möglich (wird wahrscheinlich in einer Rechnung verwendet):\n{error}",
    },
    "inventory_add_group_dialog_title": {"fa": "افزودن گروه/زیرگروه", "en": "Add Group/Subgroup", "fr": "Ajouter un groupe/sous-groupe", "de": "Gruppe/Untergruppe hinzufügen"},
    "inventory_group_type_new_main": {"fa": "این یک گروه اصلی جدید است", "en": "This is a new main group", "fr": "Ceci est un nouveau groupe principal", "de": "Dies ist eine neue Hauptgruppe"},
    "inventory_group_type_sub_for": {"fa": "زیرگروه برای: {name}", "en": "Subgroup of: {name}", "fr": "Sous-groupe de : {name}", "de": "Untergruppe von: {name}"},
    "inventory_group_type_label": {"fa": "نوع:", "en": "Type:", "fr": "Type :", "de": "Typ:"},
    "inventory_group_name_label": {"fa": "نام گروه/زیرگروه:", "en": "Group/Subgroup Name:", "fr": "Nom du groupe/sous-groupe :", "de": "Gruppen-/Untergruppenname:"},
    "save_btn": {"fa": "ذخیره", "en": "Save", "fr": "Enregistrer", "de": "Speichern"},
    "inventory_error_group_name_required": {"fa": "نام گروه الزامی است.", "en": "Group name is required.", "fr": "Le nom du groupe est obligatoire.", "de": "Gruppenname ist erforderlich."},
    "inventory_group_added_message": {"fa": "گروه/زیرگروه با موفقیت اضافه شد.", "en": "Group/subgroup added successfully.", "fr": "Groupe/sous-groupe ajouté avec succès.", "de": "Gruppe/Untergruppe erfolgreich hinzugefügt."},
    "inventory_error_add_group": {"fa": "خطا در افزودن گروه:\n{error}", "en": "Error adding group:\n{error}", "fr": "Erreur lors de l'ajout du groupe :\n{error}", "de": "Fehler beim Hinzufügen der Gruppe:\n{error}"},
    "inventory_edit_labels_dialog_title": {"fa": "ویرایش عناوین سطوح قیمت", "en": "Edit Price Tier Labels", "fr": "Modifier les libellés des niveaux de prix", "de": "Preisstufenbezeichnungen bearbeiten"},
    "inventory_price_label_row": {"fa": "عنوان قیمت شماره {n}:", "en": "Price Tier {n} Label:", "fr": "Libellé du niveau de prix {n} :", "de": "Bezeichnung Preisstufe {n}:"},
    "inventory_labels_updated_message": {
        "fa": "عناوین قیمت به‌روزرسانی شد. برای مشاهده تغییرات در تمام صفحات، برنامه را مجدد باز کنید.",
        "en": "Price labels updated. Restart the app to see the changes on every page.",
        "fr": "Libellés de prix mis à jour. Redémarrez l'application pour voir les changements partout.",
        "de": "Preisbezeichnungen aktualisiert. Starten Sie die App neu, um die Änderungen überall zu sehen.",
    },
    "success_title": {"fa": "موفق", "en": "Success", "fr": "Succès", "de": "Erfolg"},

    # ---------------- فرم افزودن/ویرایش کالا ----------------
    "product_dialog_add_title": {"fa": "افزودن کالا", "en": "Add Item", "fr": "Ajouter un article", "de": "Artikel hinzufügen"},
    "product_dialog_edit_title": {"fa": "ویرایش کالا", "en": "Edit Item", "fr": "Modifier l'article", "de": "Artikel bearbeiten"},
    "product_barcode_label": {"fa": "بارکد:", "en": "Barcode:", "fr": "Code-barres :", "de": "Barcode:"},
    "product_code_label": {"fa": "کد کالا:", "en": "Item Code:", "fr": "Code article :", "de": "Artikelcode:"},
    "product_name_label": {"fa": "نام کالا:", "en": "Item Name:", "fr": "Nom de l'article :", "de": "Artikelname:"},
    "product_unit_label": {"fa": "واحد شمارش:", "en": "Unit:", "fr": "Unité :", "de": "Einheit:"},
    "product_unit_piece": {"fa": "عدد", "en": "Piece", "fr": "Pièce", "de": "Stück"},
    "product_unit_kg": {"fa": "کیلوگرم", "en": "Kilogram", "fr": "Kilogramme", "de": "Kilogramm"},
    "product_unit_pack": {"fa": "بسته", "en": "Pack", "fr": "Paquet", "de": "Packung"},
    "product_unit_meter": {"fa": "متر", "en": "Meter", "fr": "Mètre", "de": "Meter"},
    "product_units_per_box_label": {"fa": "تعداد در جعبه:", "en": "Units per Box:", "fr": "Unités par boîte :", "de": "Einheiten pro Karton:"},
    "product_buy_price_label": {"fa": "قیمت خرید:", "en": "Buy Price:", "fr": "Prix d'achat :", "de": "Einkaufspreis:"},
    "product_main_group_label": {"fa": "گروه اصلی:", "en": "Main Group:", "fr": "Groupe principal :", "de": "Hauptgruppe:"},
    "product_sub_group_label": {"fa": "زیرگروه:", "en": "Subgroup:", "fr": "Sous-groupe :", "de": "Untergruppe:"},
    "product_no_group": {"fa": "بدون گروه", "en": "No Group", "fr": "Sans groupe", "de": "Keine Gruppe"},
    "product_no_subgroup": {"fa": "بدون زیرگروه", "en": "No Subgroup", "fr": "Sans sous-groupe", "de": "Keine Untergruppe"},
    "product_min_stock_label": {"fa": "حداقل موجودی (نقطه سفارش):", "en": "Minimum Stock (Reorder Point):", "fr": "Stock minimum (seuil de commande) :", "de": "Mindestbestand (Meldebestand):"},
    "product_default_price_tier": {"fa": "قیمت {n}", "en": "Price {n}", "fr": "Prix {n}", "de": "Preis {n}"},

    # ---------------- خزانه‌داری ----------------
    "treasury_page_title": {"fa": "خزانه‌داری", "en": "Treasury", "fr": "Trésorerie", "de": "Kasse"},
    "treasury_balance_label": {"fa": "مانده صندوق: {amount} ریال", "en": "Register Balance: {amount}", "fr": "Solde de caisse : {amount}", "de": "Kassenstand: {amount}"},
    "treasury_type_receive": {"fa": "دریافت وجه", "en": "Receive Funds", "fr": "Recevoir des fonds", "de": "Geld erhalten"},
    "treasury_type_pay": {"fa": "پرداخت وجه", "en": "Pay Funds", "fr": "Payer des fonds", "de": "Geld zahlen"},
    "treasury_type_label": {"fa": "نوع:", "en": "Type:", "fr": "Type :", "de": "Typ:"},
    "treasury_amount_label": {"fa": "مبلغ:", "en": "Amount:", "fr": "Montant :", "de": "Betrag:"},
    "treasury_description_placeholder": {
        "fa": "شرح تراکنش (اختیاری)", "en": "Transaction description (optional)",
        "fr": "Description de la transaction (facultatif)", "de": "Transaktionsbeschreibung (optional)",
    },
    "treasury_submit_btn": {"fa": "ثبت تراکنش", "en": "Submit Transaction", "fr": "Valider la transaction", "de": "Transaktion buchen"},
    "treasury_col_id": {"fa": "شناسه", "en": "ID", "fr": "ID", "de": "ID"},
    "treasury_col_type": {"fa": "نوع", "en": "Type", "fr": "Type", "de": "Typ"},
    "treasury_col_amount": {"fa": "مبلغ", "en": "Amount", "fr": "Montant", "de": "Betrag"},
    "treasury_col_date": {"fa": "تاریخ", "en": "Date", "fr": "Date", "de": "Datum"},
    "treasury_col_description": {"fa": "شرح", "en": "Description", "fr": "Description", "de": "Beschreibung"},
    "treasury_row_receive": {"fa": "دریافت", "en": "Received", "fr": "Reçu", "de": "Erhalten"},
    "treasury_row_pay": {"fa": "پرداخت", "en": "Paid", "fr": "Payé", "de": "Bezahlt"},
    "treasury_error_amount": {"fa": "مبلغ باید بزرگ‌تر از صفر باشد.", "en": "Amount must be greater than zero.", "fr": "Le montant doit être supérieur à zéro.", "de": "Der Betrag muss größer als null sein."},
    "treasury_error_no_box": {
        "fa": "برای ثبت تراکنش خزانه باید یک صندوق فعال داشته باشید.",
        "en": "You must have an active register to submit a treasury transaction.",
        "fr": "Vous devez avoir une caisse active pour valider une transaction de trésorerie.",
        "de": "Sie müssen eine aktive Kasse haben, um eine Kassentransaktion zu buchen.",
    },
    "treasury_error_submit": {"fa": "خطا در ثبت تراکنش:\n{error}", "en": "Error submitting transaction:\n{error}", "fr": "Erreur lors de la validation de la transaction :\n{error}", "de": "Fehler beim Buchen der Transaktion:\n{error}"},

    # ---------------- مشتریان ----------------
    "customers_page_title": {"fa": "مشتریان", "en": "Customers", "fr": "Clients", "de": "Kunden"},
    "customers_tab_list": {"fa": "لیست مشتریان", "en": "Customer List", "fr": "Liste des clients", "de": "Kundenliste"},
    "customers_tab_bulk_sms": {"fa": "پیامک گروهی", "en": "Bulk SMS", "fr": "SMS groupé", "de": "Massen-SMS"},
    "customers_tab_inactive": {"fa": "مشتریان غیرفعال", "en": "Inactive Customers", "fr": "Clients inactifs", "de": "Inaktive Kunden"},
    "customers_add_dialog_title": {"fa": "افزودن مشتری جدید", "en": "Add New Customer", "fr": "Ajouter un nouveau client", "de": "Neuen Kunden hinzufügen"},
    "customers_name_label": {"fa": "نام مشتری:", "en": "Customer Name:", "fr": "Nom du client :", "de": "Kundenname:"},
    "customers_phone_label": {"fa": "شماره موبایل:", "en": "Mobile Number:", "fr": "Numéro de mobile :", "de": "Handynummer:"},
    "sms_compose_dialog_title": {"fa": "ارسال پیامک", "en": "Send SMS", "fr": "Envoyer un SMS", "de": "SMS senden"},
    "sms_recipients_count": {"fa": "گیرندگان: {n} نفر", "en": "Recipients: {n}", "fr": "Destinataires : {n}", "de": "Empfänger: {n}"},
    "sms_names_more": {"fa": "و {n} نفر دیگر", "en": "and {n} more", "fr": "et {n} de plus", "de": "und {n} weitere"},
    "sms_message_placeholder": {"fa": "متن پیامک را اینجا بنویسید...", "en": "Write the SMS text here...", "fr": "Écrivez le texte du SMS ici...", "de": "SMS-Text hier eingeben..."},
    "sms_send_btn": {"fa": "ارسال", "en": "Send", "fr": "Envoyer", "de": "Senden"},
    "sms_error_empty_message": {"fa": "متن پیامک نمی‌تواند خالی باشد.", "en": "SMS text cannot be empty.", "fr": "Le texte du SMS ne peut pas être vide.", "de": "SMS-Text darf nicht leer sein."},
    "sms_error_no_recipients": {"fa": "هیچ گیرنده‌ای انتخاب نشده است.", "en": "No recipient has been selected.", "fr": "Aucun destinataire n'a été sélectionné.", "de": "Kein Empfänger ausgewählt."},
    "sms_result_summary": {"fa": "از {total} پیام: {sent} مورد با موفقیت ارسال شد.", "en": "Of {total} messages: {sent} were sent successfully.", "fr": "Sur {total} messages : {sent} envoyés avec succès.", "de": "Von {total} Nachrichten: {sent} erfolgreich gesendet."},
    "sms_result_not_configured": {
        "fa": "⚠️ {n} مورد ارسال نشد چون سرویس پیامک هنوز پیکربندی نشده.",
        "en": "⚠️ {n} were not sent because the SMS service is not configured yet.",
        "fr": "⚠️ {n} n'ont pas été envoyés car le service SMS n'est pas encore configuré.",
        "de": "⚠️ {n} wurden nicht gesendet, da der SMS-Dienst noch nicht konfiguriert ist.",
    },
    "sms_result_failed": {"fa": "❌ {n} مورد به دلیل خطای سرویس‌دهنده ارسال نشد.", "en": "❌ {n} failed to send due to a provider error.", "fr": "❌ {n} n'ont pas pu être envoyés en raison d'une erreur du fournisseur.", "de": "❌ {n} konnten aufgrund eines Anbieterfehlers nicht gesendet werden."},
    "sms_result_no_requests_lib": {
        "fa": "⚠️ {n} مورد ارسال نشد چون کتابخانه requests نصب نیست ('pip install requests').",
        "en": "⚠️ {n} were not sent because the requests library is not installed ('pip install requests').",
        "fr": "⚠️ {n} n'ont pas été envoyés car la bibliothèque requests n'est pas installée (« pip install requests »).",
        "de": "⚠️ {n} wurden nicht gesendet, da die requests-Bibliothek nicht installiert ist ('pip install requests').",
    },
    "sms_result_title": {"fa": "نتیجه ارسال", "en": "Send Result", "fr": "Résultat de l'envoi", "de": "Sendeergebnis"},
    "customers_search_placeholder": {
        "fa": "جستجو بر اساس نام یا شماره موبایل...", "en": "Search by name or mobile number...",
        "fr": "Rechercher par nom ou numéro de mobile...", "de": "Suche nach Name oder Handynummer...",
    },
    "customers_add_btn": {"fa": "+ مشتری جدید", "en": "+ New Customer", "fr": "+ Nouveau client", "de": "+ Neuer Kunde"},
    "customers_col_id": {"fa": "شناسه", "en": "ID", "fr": "ID", "de": "ID"},
    "customers_col_name": {"fa": "نام", "en": "Name", "fr": "Nom", "de": "Name"},
    "customers_col_phone": {"fa": "موبایل", "en": "Mobile", "fr": "Mobile", "de": "Handy"},
    "customers_col_balance": {"fa": "مانده حساب", "en": "Balance", "fr": "Solde", "de": "Saldo"},
    "customers_history_placeholder": {
        "fa": "برای دیدن تاریخچه‌ی خرید، یک مشتری را از لیست انتخاب کنید.",
        "en": "Select a customer from the list to view their purchase history.",
        "fr": "Sélectionnez un client dans la liste pour voir son historique d'achats.",
        "de": "Wählen Sie einen Kunden aus der Liste, um den Kaufverlauf zu sehen.",
    },
    "customers_history_title": {"fa": "فاکتورهای فروش یک سال اخیر «{name}»:", "en": "Sales invoices in the last year for \"{name}\":", "fr": "Factures de vente de la dernière année pour « {name} » :", "de": "Verkaufsrechnungen des letzten Jahres für „{name}“:"},
    "customers_invoice_col_number": {"fa": "شماره فاکتور", "en": "Invoice Number", "fr": "Numéro de facture", "de": "Rechnungsnummer"},
    "customers_invoice_col_date": {"fa": "تاریخ", "en": "Date", "fr": "Date", "de": "Datum"},
    "customers_invoice_col_payment": {"fa": "نوع پرداخت", "en": "Payment Type", "fr": "Mode de paiement", "de": "Zahlungsart"},
    "customers_invoice_col_total": {"fa": "مبلغ کل", "en": "Total Amount", "fr": "Montant total", "de": "Gesamtbetrag"},
    "customers_sms_to_selected_btn": {"fa": "ارسال پیامک به این مشتری", "en": "Send SMS to This Customer", "fr": "Envoyer un SMS à ce client", "de": "SMS an diesen Kunden senden"},
    "customers_error_both_required": {"fa": "نام و شماره موبایل هر دو الزامی است.", "en": "Both name and mobile number are required.", "fr": "Le nom et le numéro de mobile sont tous deux obligatoires.", "de": "Name und Handynummer sind beide erforderlich."},
    "customers_error_duplicate_phone": {
        "fa": "مشتری‌ای با این شماره موبایل قبلاً ثبت شده است.", "en": "A customer with this mobile number is already registered.",
        "fr": "Un client avec ce numéro de mobile est déjà enregistré.", "de": "Ein Kunde mit dieser Handynummer ist bereits registriert.",
    },
    "customers_select_first": {"fa": "لطفاً ابتدا یک مشتری را از لیست انتخاب کنید.", "en": "Please select a customer from the list first.", "fr": "Veuillez d'abord sélectionner un client dans la liste.", "de": "Bitte zuerst einen Kunden aus der Liste auswählen."},
    "customers_error_no_phone": {"fa": "این مشتری شماره موبایل ثبت‌شده‌ای ندارد.", "en": "This customer has no registered mobile number.", "fr": "Ce client n'a pas de numéro de mobile enregistré.", "de": "Dieser Kunde hat keine registrierte Handynummer."},
    "customers_bulk_access_denied": {
        "fa": "دسترسی به پیامک گروهی فقط برای مدیر فروشگاه و حسابدار مجاز است.",
        "en": "Bulk SMS access is only allowed for the store manager and accountant.",
        "fr": "L'accès au SMS groupé est réservé au gérant et au comptable.",
        "de": "Massen-SMS-Zugriff ist nur dem Filialleiter und Buchhalter erlaubt.",
    },
    "customers_bulk_info": {
        "fa": "پیامک زیر برای تمام مشتریان ثبت‌شده در سیستم ارسال می‌شود.",
        "en": "The message below will be sent to every customer registered in the system.",
        "fr": "Le message ci-dessous sera envoyé à tous les clients enregistrés dans le système.",
        "de": "Die folgende Nachricht wird an alle im System registrierten Kunden gesendet.",
    },
    "customers_total_count": {"fa": "تعداد کل مشتریان: {n} نفر", "en": "Total customers: {n}", "fr": "Nombre total de clients : {n}", "de": "Kunden insgesamt: {n}"},
    "customers_bulk_compose_btn": {"fa": "نوشتن و ارسال پیامک گروهی", "en": "Write & Send Bulk SMS", "fr": "Rédiger et envoyer un SMS groupé", "de": "Massen-SMS schreiben und senden"},
    "customers_no_phone_customers": {
        "fa": "هیچ مشتری‌ای با شماره موبایل ثبت‌شده وجود ندارد.", "en": "No customer with a registered mobile number exists.",
        "fr": "Aucun client n'a de numéro de mobile enregistré.", "de": "Kein Kunde mit registrierter Handynummer vorhanden.",
    },
    "customers_inactive_access_denied": {
        "fa": "دسترسی به این بخش فقط برای مدیر فروشگاه و صندوق‌دار مجاز است.",
        "en": "Access to this section is only allowed for the store manager and cashier.",
        "fr": "L'accès à cette section est réservé au gérant et au caissier.",
        "de": "Der Zugriff auf diesen Bereich ist nur dem Filialleiter und Kassierer erlaubt.",
    },
    "customers_inactive_info": {
        "fa": "مشتریانی که در بازه‌ی زیر هیچ خریدی نداشته‌اند را پیدا و به آن‌ها پیامک بفرستید.",
        "en": "Find customers who made no purchase in the range below and message them.",
        "fr": "Trouvez les clients qui n'ont fait aucun achat dans la période ci-dessous et envoyez-leur un message.",
        "de": "Finden Sie Kunden ohne Einkauf im untenstehenden Zeitraum und senden Sie ihnen eine Nachricht.",
    },
    "customers_date_from_label": {"fa": "از تاریخ:", "en": "From Date:", "fr": "Date de début :", "de": "Von Datum:"},
    "customers_date_to_label": {"fa": "تا تاریخ:", "en": "To Date:", "fr": "Date de fin :", "de": "Bis Datum:"},
    "customers_sms_to_all_found_btn": {"fa": "ارسال پیامک به همه‌ی نتایج بالا", "en": "Send SMS to All Results Above", "fr": "Envoyer un SMS à tous les résultats ci-dessus", "de": "SMS an alle obigen Ergebnisse senden"},
    "customers_search_first": {
        "fa": "ابتدا جستجو کنید تا نتیجه‌ای برای ارسال پیامک وجود داشته باشد.",
        "en": "Search first so there are results to send an SMS to.",
        "fr": "Effectuez d'abord une recherche pour avoir des résultats auxquels envoyer un SMS.",
        "de": "Zuerst suchen, damit Ergebnisse für den SMS-Versand vorliegen.",
    },
    "customers_no_phone_results": {
        "fa": "هیچ‌کدام از نتایج شماره موبایل ثبت‌شده ندارند.", "en": "None of the results have a registered mobile number.",
        "fr": "Aucun des résultats n'a de numéro de mobile enregistré.", "de": "Keines der Ergebnisse hat eine registrierte Handynummer.",
    },

    # ---------------- تاریخچه فاکتورها ----------------
    "invoices_page_title": {"fa": "تاریخچه فاکتورها", "en": "Invoice History", "fr": "Historique des factures", "de": "Rechnungsverlauf"},
    "invoices_type_filter_label": {"fa": "نوع:", "en": "Type:", "fr": "Type :", "de": "Typ:"},
    "invoices_type_all": {"fa": "همه", "en": "All", "fr": "Tous", "de": "Alle"},
    "invoice_type_sale": {"fa": "فروش", "en": "Sale", "fr": "Vente", "de": "Verkauf"},
    "invoice_type_purchase": {"fa": "خرید", "en": "Purchase", "fr": "Achat", "de": "Einkauf"},
    "invoices_search_placeholder": {
        "fa": "جستجو در شماره فاکتور یا نام طرف حساب...", "en": "Search invoice number or party name...",
        "fr": "Rechercher un numéro de facture ou un nom de tiers...", "de": "Rechnungsnummer oder Namen suchen...",
    },
    "invoices_col_id": {"fa": "شناسه", "en": "ID", "fr": "ID", "de": "ID"},
    "invoices_col_number": {"fa": "شماره فاکتور", "en": "Invoice Number", "fr": "Numéro de facture", "de": "Rechnungsnummer"},
    "invoices_col_type": {"fa": "نوع", "en": "Type", "fr": "Type", "de": "Typ"},
    "invoices_col_date": {"fa": "تاریخ", "en": "Date", "fr": "Date", "de": "Datum"},
    "invoices_col_party": {"fa": "طرف حساب", "en": "Party", "fr": "Tiers", "de": "Partei"},
    "invoices_col_payment": {"fa": "نوع پرداخت", "en": "Payment Type", "fr": "Mode de paiement", "de": "Zahlungsart"},
    "invoices_col_total": {"fa": "مبلغ کل", "en": "Total Amount", "fr": "Montant total", "de": "Gesamtbetrag"},
    "invoices_col_registered_by": {"fa": "ثبت‌کننده", "en": "Registered By", "fr": "Enregistré par", "de": "Erfasst von"},
    "invoices_view_details_btn": {"fa": "مشاهده جزئیات", "en": "View Details", "fr": "Voir les détails", "de": "Details anzeigen"},
    "invoices_delete_btn": {"fa": "حذف فاکتور", "en": "Delete Invoice", "fr": "Supprimer la facture", "de": "Rechnung löschen"},
    "invoices_select_first": {"fa": "لطفاً ابتدا یک فاکتور را از لیست انتخاب کنید.", "en": "Please select an invoice from the list first.", "fr": "Veuillez d'abord sélectionner une facture dans la liste.", "de": "Bitte zuerst eine Rechnung aus der Liste auswählen."},
    "invoices_confirm_delete_title": {"fa": "تایید حذف", "en": "Confirm Delete", "fr": "Confirmer la suppression", "de": "Löschen bestätigen"},
    "invoices_confirm_delete_message": {
        "fa": "با حذف این فاکتور، موجودی انبار، مانده‌ی حساب طرف، تراکنش خزانه و سند حسابداری مرتبط با آن هم برگردانده می‌شوند. این عملیات قابل بازگشت نیست.\n\nآیا مطمئن هستید؟",
        "en": "Deleting this invoice will also reverse the stock, party balance, treasury transaction, and related journal entry. This action cannot be undone.\n\nAre you sure?",
        "fr": "La suppression de cette facture annulera également le stock, le solde du tiers, la transaction de trésorerie et l'écriture comptable associée. Cette action est irréversible.\n\nÊtes-vous sûr(e) ?",
        "de": "Das Löschen dieser Rechnung macht auch Bestand, Partei-Saldo, Kassentransaktion und den zugehörigen Buchungssatz rückgängig. Dies kann nicht rückgängig gemacht werden.\n\nSind Sie sicher?",
    },
    "invoices_delete_success": {
        "fa": "فاکتور و همه‌ی اثرات جانبی آن با موفقیت حذف شد.", "en": "The invoice and all its side effects were successfully deleted.",
        "fr": "La facture et tous ses effets connexes ont été supprimés avec succès.", "de": "Die Rechnung und alle Nebeneffekte wurden erfolgreich gelöscht.",
    },
    "invoices_delete_error": {"fa": "خطا در حذف فاکتور:\n{error}", "en": "Error deleting invoice:\n{error}", "fr": "Erreur lors de la suppression de la facture :\n{error}", "de": "Fehler beim Löschen der Rechnung:\n{error}"},
    "invoices_details_dialog_title": {"fa": "جزئیات فاکتور {number}", "en": "Details of Invoice {number}", "fr": "Détails de la facture {number}", "de": "Details der Rechnung {number}"},
    "invoices_details_header": {
        "fa": "شماره فاکتور: {number}   |   تاریخ: {date}   |   نوع پرداخت: {payment}",
        "en": "Invoice: {number}   |   Date: {date}   |   Payment: {payment}",
        "fr": "Facture : {number}   |   Date : {date}   |   Paiement : {payment}",
        "de": "Rechnung: {number}   |   Datum: {date}   |   Zahlung: {payment}",
    },
    "invoices_details_party": {"fa": "طرف حساب: {name}", "en": "Party: {name}", "fr": "Tiers : {name}", "de": "Partei: {name}"},
    "invoices_details_col_code": {"fa": "کد کالا", "en": "Item Code", "fr": "Code article", "de": "Artikelcode"},
    "invoices_details_col_name": {"fa": "نام کالا", "en": "Item Name", "fr": "Nom de l'article", "de": "Artikelname"},
    "invoices_details_col_qty": {"fa": "تعداد", "en": "Qty", "fr": "Quantité", "de": "Menge"},
    "invoices_details_col_price": {"fa": "قیمت واحد", "en": "Unit Price", "fr": "Prix unitaire", "de": "Einzelpreis"},
    "invoices_details_col_total": {"fa": "جمع سطر", "en": "Line Total", "fr": "Total ligne", "de": "Zeilensumme"},
    "invoices_details_total": {"fa": "مبلغ کل فاکتور: {amount} ریال", "en": "Invoice Total: {amount}", "fr": "Total de la facture : {amount}", "de": "Rechnungssumme: {amount}"},
    "close_btn": {"fa": "بستن", "en": "Close", "fr": "Fermer", "de": "Schließen"},

    # ---------------- چک‌ها ----------------
    "checks_page_title": {"fa": "مدیریت چک‌ها", "en": "Check Management", "fr": "Gestion des chèques", "de": "Scheckverwaltung"},
    "checks_status_pending": {"fa": "در انتظار وصول", "en": "Pending Collection", "fr": "En attente d'encaissement", "de": "Ausstehend"},
    "checks_status_collected": {"fa": "وصول‌شده", "en": "Collected", "fr": "Encaissé", "de": "Eingezogen"},
    "checks_status_bounced": {"fa": "برگشت‌خورده", "en": "Bounced", "fr": "Rejeté", "de": "Geplatzt"},
    "checks_status_transferred": {"fa": "انتقال‌یافته", "en": "Transferred", "fr": "Transféré", "de": "Übertragen"},
    "checks_number_placeholder": {"fa": "شماره چک", "en": "Check Number", "fr": "Numéro de chèque", "de": "Schecknummer"},
    "checks_bank_placeholder": {"fa": "نام بانک", "en": "Bank Name", "fr": "Nom de la banque", "de": "Bankname"},
    "checks_direction_received": {"fa": "دریافتی (از مشتری)", "en": "Received (from customer)", "fr": "Reçu (du client)", "de": "Erhalten (vom Kunden)"},
    "checks_direction_issued": {"fa": "پرداختی (به تامین‌کننده)", "en": "Issued (to supplier)", "fr": "Émis (au fournisseur)", "de": "Ausgestellt (an Lieferant)"},
    "checks_register_btn": {"fa": "+ ثبت چک", "en": "+ Register Check", "fr": "+ Enregistrer un chèque", "de": "+ Scheck registrieren"},
    "checks_col_id": {"fa": "شناسه", "en": "ID", "fr": "ID", "de": "ID"},
    "checks_col_number": {"fa": "شماره چک", "en": "Check Number", "fr": "Numéro de chèque", "de": "Schecknummer"},
    "checks_col_bank": {"fa": "بانک", "en": "Bank", "fr": "Banque", "de": "Bank"},
    "checks_col_amount": {"fa": "مبلغ", "en": "Amount", "fr": "Montant", "de": "Betrag"},
    "checks_col_due_date": {"fa": "سررسید", "en": "Due Date", "fr": "Échéance", "de": "Fälligkeit"},
    "checks_col_type": {"fa": "نوع", "en": "Type", "fr": "Type", "de": "Typ"},
    "checks_col_status": {"fa": "وضعیت", "en": "Status", "fr": "Statut", "de": "Status"},
    "checks_row_received": {"fa": "دریافتی", "en": "Received", "fr": "Reçu", "de": "Erhalten"},
    "checks_row_issued": {"fa": "پرداختی", "en": "Issued", "fr": "Émis", "de": "Ausgestellt"},
    "checks_collect_btn": {"fa": "وصول چک انتخاب‌شده", "en": "Collect Selected Check", "fr": "Encaisser le chèque sélectionné", "de": "Ausgewählten Scheck einziehen"},
    "checks_bounce_btn": {"fa": "ثبت برگشت خوردن", "en": "Mark as Bounced", "fr": "Marquer comme rejeté", "de": "Als geplatzt markieren"},
    "checks_edit_btn": {"fa": "ویرایش چک", "en": "Edit Check", "fr": "Modifier le chèque", "de": "Scheck bearbeiten"},
    "checks_delete_btn": {"fa": "حذف چک", "en": "Delete Check", "fr": "Supprimer le chèque", "de": "Scheck löschen"},
    "checks_error_required": {"fa": "شماره چک و مبلغ الزامی است.", "en": "Check number and amount are required.", "fr": "Le numéro de chèque et le montant sont obligatoires.", "de": "Schecknummer und Betrag sind erforderlich."},
    "checks_error_no_box": {
        "fa": "کاربر ادمین باید یک صندوق فعال برای ثبت چک انتخاب کند.", "en": "Admin must select an active register to register a check.",
        "fr": "L'administrateur doit sélectionner une caisse active pour enregistrer un chèque.", "de": "Der Administrator muss eine aktive Kasse für die Scheckregistrierung auswählen.",
    },
    "checks_error_register": {"fa": "خطا در ثبت چک:\n{error}", "en": "Error registering check:\n{error}", "fr": "Erreur lors de l'enregistrement du chèque :\n{error}", "de": "Fehler beim Registrieren des Schecks:\n{error}"},
    "checks_select_first": {"fa": "لطفاً ابتدا یک چک را انتخاب کنید.", "en": "Please select a check first.", "fr": "Veuillez d'abord sélectionner un chèque.", "de": "Bitte zuerst einen Scheck auswählen."},
    "checks_collect_success": {
        "fa": "چک با موفقیت وصول شد و در خزانه ثبت گردید.", "en": "Check collected successfully and recorded in the treasury.",
        "fr": "Chèque encaissé avec succès et enregistré en trésorerie.", "de": "Scheck erfolgreich eingezogen und in der Kasse erfasst.",
    },
    "checks_confirm_title": {"fa": "تایید", "en": "Confirm", "fr": "Confirmer", "de": "Bestätigen"},
    "checks_confirm_bounce": {"fa": "آیا از ثبت برگشت خوردن این چک مطمئن هستید؟", "en": "Are you sure you want to mark this check as bounced?", "fr": "Voulez-vous vraiment marquer ce chèque comme rejeté ?", "de": "Möchten Sie diesen Scheck wirklich als geplatzt markieren?"},
    "checks_edit_dialog_title": {"fa": "ویرایش چک", "en": "Edit Check", "fr": "Modifier le chèque", "de": "Scheck bearbeiten"},
    "checks_number_label": {"fa": "شماره چک:", "en": "Check Number:", "fr": "Numéro de chèque :", "de": "Schecknummer:"},
    "checks_bank_label": {"fa": "بانک:", "en": "Bank:", "fr": "Banque :", "de": "Bank:"},
    "checks_amount_label": {"fa": "مبلغ:", "en": "Amount:", "fr": "Montant :", "de": "Betrag:"},
    "checks_due_date_label": {"fa": "سررسید:", "en": "Due Date:", "fr": "Échéance :", "de": "Fälligkeit:"},
    "checks_description_label": {"fa": "شرح:", "en": "Description:", "fr": "Description :", "de": "Beschreibung:"},
    "checks_confirm_delete": {"fa": "آیا از حذف این چک اطمینان دارید؟", "en": "Are you sure you want to delete this check?", "fr": "Voulez-vous vraiment supprimer ce chèque ?", "de": "Möchten Sie diesen Scheck wirklich löschen?"},

    # ---------------- حسابداری ----------------
    "accounting_page_title": {"fa": "حسابداری", "en": "Accounting", "fr": "Comptabilité", "de": "Buchhaltung"},
    "accounting_access_denied": {
        "fa": "دسترسی به ماژول حسابداری فقط برای مدیر فروشگاه و حسابدار مجاز است.",
        "en": "Access to the accounting module is only allowed for the store manager and accountant.",
        "fr": "L'accès au module de comptabilité est réservé au gérant et au comptable.",
        "de": "Der Zugriff auf das Buchhaltungsmodul ist nur dem Filialleiter und Buchhalter erlaubt.",
    },
    "accounting_tab_chart": {"fa": "سرفصل حسابها", "en": "Chart of Accounts", "fr": "Plan comptable", "de": "Kontenplan"},
    "accounting_tab_journal": {"fa": "صدور سند", "en": "Journal Entry", "fr": "Écriture comptable", "de": "Buchungssatz"},
    "accounting_tab_ledger": {"fa": "دفتر کل", "en": "General Ledger", "fr": "Grand livre", "de": "Hauptbuch"},
    "accounting_tab_trial_balance": {"fa": "تراز آزمایشی", "en": "Trial Balance", "fr": "Balance de vérification", "de": "Saldenliste"},
    "accounting_tab_profit_loss": {"fa": "سود و زیان", "en": "Profit & Loss", "fr": "Résultat", "de": "Gewinn & Verlust"},
    "accounting_tab_balance_sheet": {"fa": "ترازنامه", "en": "Balance Sheet", "fr": "Bilan", "de": "Bilanz"},
    "accounting_tab_modian": {"fa": "اسناد ارسال به سامانه مودیان", "en": "Modian Submission Documents", "fr": "Documents pour le système fiscal", "de": "Modian-Übermittlungsdokumente"},

    "account_type_asset": {"fa": "دارایی", "en": "Asset", "fr": "Actif", "de": "Vermögenswert"},
    "account_type_liability": {"fa": "بدهی", "en": "Liability", "fr": "Passif", "de": "Verbindlichkeit"},
    "account_type_equity": {"fa": "سرمایه", "en": "Equity", "fr": "Capitaux propres", "de": "Eigenkapital"},
    "account_type_revenue": {"fa": "درآمد", "en": "Revenue", "fr": "Revenu", "de": "Ertrag"},
    "account_type_expense": {"fa": "هزینه", "en": "Expense", "fr": "Dépense", "de": "Aufwand"},

    "accounting_code_placeholder": {"fa": "کد حساب (مثلاً 1300)", "en": "Account code (e.g. 1300)", "fr": "Code de compte (ex. 1300)", "de": "Kontocode (z. B. 1300)"},
    "accounting_name_placeholder": {"fa": "نام حساب", "en": "Account name", "fr": "Nom du compte", "de": "Kontoname"},
    "accounting_add_account_btn": {"fa": "+ افزودن حساب", "en": "+ Add Account", "fr": "+ Ajouter un compte", "de": "+ Konto hinzufügen"},
    "accounting_col_code": {"fa": "کد", "en": "Code", "fr": "Code", "de": "Code"},
    "accounting_col_account_name": {"fa": "نام حساب", "en": "Account Name", "fr": "Nom du compte", "de": "Kontoname"},
    "accounting_col_type": {"fa": "نوع", "en": "Type", "fr": "Type", "de": "Typ"},
    "accounting_error_code_name_required": {"fa": "کد و نام حساب الزامی است.", "en": "Account code and name are required.", "fr": "Le code et le nom du compte sont obligatoires.", "de": "Kontocode und -name sind erforderlich."},
    "accounting_error_add_account": {
        "fa": "خطا در افزودن حساب (احتمالاً کد تکراری است):\n{error}",
        "en": "Error adding account (the code is probably duplicated):\n{error}",
        "fr": "Erreur lors de l'ajout du compte (le code est probablement en double) :\n{error}",
        "de": "Fehler beim Hinzufügen des Kontos (Code wahrscheinlich doppelt):\n{error}",
    },

    "accounting_description_placeholder": {"fa": "شرح سند...", "en": "Entry description...", "fr": "Description de l'écriture...", "de": "Buchungsbeschreibung..."},
    "accounting_account_label": {"fa": "حساب:", "en": "Account:", "fr": "Compte :", "de": "Konto:"},
    "accounting_debit_label": {"fa": "بدهکار:", "en": "Debit:", "fr": "Débit :", "de": "Soll:"},
    "accounting_credit_label": {"fa": "بستانکار:", "en": "Credit:", "fr": "Crédit :", "de": "Haben:"},
    "accounting_add_line_btn": {"fa": "+ افزودن ردیف", "en": "+ Add Line", "fr": "+ Ajouter une ligne", "de": "+ Zeile hinzufügen"},
    "accounting_balance_label": {"fa": "جمع بدهکار: {debit} | جمع بستانکار: {credit}", "en": "Total Debit: {debit} | Total Credit: {credit}", "fr": "Total débit : {debit} | Total crédit : {credit}", "de": "Summe Soll: {debit} | Summe Haben: {credit}"},
    "accounting_submit_entry_btn": {"fa": "ثبت سند", "en": "Submit Entry", "fr": "Valider l'écriture", "de": "Buchung erfassen"},
    "accounting_error_line_amount": {
        "fa": "حداقل یکی از مقادیر بدهکار یا بستانکار باید بزرگ‌تر از صفر باشد.",
        "en": "At least one of debit or credit must be greater than zero.",
        "fr": "Au moins l'une des valeurs débit ou crédit doit être supérieure à zéro.",
        "de": "Mindestens Soll oder Haben muss größer als null sein.",
    },
    "accounting_error_line_both": {
        "fa": "هر ردیف فقط می‌تواند یا بدهکار یا بستانکار باشد، نه هر دو.",
        "en": "Each line can only be a debit or a credit, not both.",
        "fr": "Chaque ligne ne peut être que débit ou crédit, pas les deux.",
        "de": "Jede Zeile kann nur Soll oder Haben sein, nicht beides.",
    },
    "accounting_error_min_lines": {"fa": "سند باید حداقل ۲ ردیف داشته باشد.", "en": "An entry must have at least 2 lines.", "fr": "Une écriture doit comporter au moins 2 lignes.", "de": "Eine Buchung muss mindestens 2 Zeilen haben."},
    "accounting_entry_success": {"fa": "سند شماره {number} با موفقیت ثبت شد.", "en": "Entry {number} was submitted successfully.", "fr": "L'écriture {number} a été enregistrée avec succès.", "de": "Buchung {number} wurde erfolgreich erfasst."},
    "accounting_unbalanced_title": {"fa": "سند نامتوازن", "en": "Unbalanced Entry", "fr": "Écriture déséquilibrée", "de": "Unausgeglichene Buchung"},
    "accounting_error_submit_entry": {"fa": "خطا در ثبت سند:\n{error}", "en": "Error submitting entry:\n{error}", "fr": "Erreur lors de la validation de l'écriture :\n{error}", "de": "Fehler beim Erfassen der Buchung:\n{error}"},

    "accounting_show_ledger_btn": {"fa": "نمایش دفتر کل", "en": "Show General Ledger", "fr": "Afficher le grand livre", "de": "Hauptbuch anzeigen"},
    "accounting_col_date": {"fa": "تاریخ", "en": "Date", "fr": "Date", "de": "Datum"},
    "accounting_col_entry_number": {"fa": "شماره سند", "en": "Entry Number", "fr": "Numéro d'écriture", "de": "Buchungsnummer"},
    "accounting_col_debit": {"fa": "بدهکار", "en": "Debit", "fr": "Débit", "de": "Soll"},
    "accounting_col_credit": {"fa": "بستانکار", "en": "Credit", "fr": "Crédit", "de": "Haben"},
    "accounting_col_balance": {"fa": "مانده", "en": "Balance", "fr": "Solde", "de": "Saldo"},

    "accounting_refresh_btn": {"fa": "به‌روزرسانی", "en": "Refresh", "fr": "Actualiser", "de": "Aktualisieren"},
    "accounting_col_total_debit": {"fa": "جمع بدهکار", "en": "Total Debit", "fr": "Total débit", "de": "Summe Soll"},
    "accounting_col_total_credit": {"fa": "جمع بستانکار", "en": "Total Credit", "fr": "Total crédit", "de": "Summe Haben"},

    "accounting_date_from_label": {"fa": "از تاریخ:", "en": "From Date:", "fr": "Date de début :", "de": "Von Datum:"},
    "accounting_date_to_label": {"fa": "تا تاریخ:", "en": "To Date:", "fr": "Date de fin :", "de": "Bis Datum:"},
    "accounting_calc_pl_btn": {"fa": "محاسبه سود و زیان", "en": "Calculate Profit & Loss", "fr": "Calculer le résultat", "de": "Gewinn & Verlust berechnen"},
    "accounting_col_account": {"fa": "حساب", "en": "Account", "fr": "Compte", "de": "Konto"},
    "accounting_col_amount": {"fa": "مبلغ", "en": "Amount", "fr": "Montant", "de": "Betrag"},
    "accounting_revenue_row": {"fa": "درآمد - {name}", "en": "Revenue - {name}", "fr": "Revenu - {name}", "de": "Ertrag - {name}"},
    "accounting_expense_row": {"fa": "هزینه - {name}", "en": "Expense - {name}", "fr": "Dépense - {name}", "de": "Aufwand - {name}"},
    "accounting_pl_result": {
        "fa": "جمع درآمد: {revenue} | جمع هزینه: {expense} | سود خالص: {profit}",
        "en": "Total Revenue: {revenue} | Total Expense: {expense} | Net Profit: {profit}",
        "fr": "Total revenus : {revenue} | Total dépenses : {expense} | Résultat net : {profit}",
        "de": "Summe Ertrag: {revenue} | Summe Aufwand: {expense} | Nettogewinn: {profit}",
    },

    "accounting_calc_balance_sheet_btn": {"fa": "محاسبه ترازنامه (تا امروز)", "en": "Calculate Balance Sheet (to date)", "fr": "Calculer le bilan (à ce jour)", "de": "Bilanz berechnen (bis heute)"},
    "accounting_col_running_balance": {"fa": "مانده", "en": "Balance", "fr": "Solde", "de": "Saldo"},
    "accounting_bs_result": {
        "fa": "جمع دارایی: {assets} | جمع بدهی: {liabilities} | جمع سرمایه: {equity}",
        "en": "Total Assets: {assets} | Total Liabilities: {liabilities} | Total Equity: {equity}",
        "fr": "Total actif : {assets} | Total passif : {liabilities} | Total capitaux propres : {equity}",
        "de": "Summe Vermögen: {assets} | Summe Verbindlichkeiten: {liabilities} | Summe Eigenkapital: {equity}",
    },

    "modian_warning_note": {
        "fa": "⚠️ این بخش فقط ساختار داده صورتحساب الکترونیکی را آماده می‌کند. اتصال واقعی به سامانه مودیان نیازمند گواهی دیجیتال و API رسمی سازمان امور مالیاتی است که در این نسخه پیاده‌سازی نشده.",
        "en": "⚠️ This section only prepares the electronic invoice data structure. A real connection to the Modian system requires a digital certificate and the official tax authority API, which is not implemented in this version.",
        "fr": "⚠️ Cette section prépare uniquement la structure de données de la facture électronique. Une connexion réelle au système fiscal nécessite un certificat numérique et l'API officielle de l'administration fiscale, non implémentée dans cette version.",
        "de": "⚠️ Dieser Abschnitt bereitet nur die Datenstruktur der elektronischen Rechnung vor. Eine echte Verbindung zum Modian-System erfordert ein digitales Zertifikat und die offizielle Steuerbehörden-API, die in dieser Version nicht implementiert ist.",
    },
    "modian_api_link_label": {"fa": "لینک API سامانه مودیان:", "en": "Modian System API Link:", "fr": "Lien API du système fiscal :", "de": "Modian-System-API-Link:"},
    "modian_api_placeholder": {"fa": "مثلاً: https://tp.tax.gov.ir/api/...", "en": "e.g. https://tp.tax.gov.ir/api/...", "fr": "ex. https://tp.tax.gov.ir/api/...", "de": "z. B. https://tp.tax.gov.ir/api/..."},
    "modian_cert_link_label": {"fa": "لینک گواهی دیجیتال:", "en": "Digital Certificate Link:", "fr": "Lien du certificat numérique :", "de": "Digitaler Zertifikatslink:"},
    "modian_cert_placeholder": {"fa": "لینک گواهی دیجیتال", "en": "Digital certificate link", "fr": "Lien du certificat numérique", "de": "Link zum digitalen Zertifikat"},
    "modian_save_settings_btn": {"fa": "ذخیره تنظیمات اتصال", "en": "Save Connection Settings", "fr": "Enregistrer les paramètres de connexion", "de": "Verbindungseinstellungen speichern"},
    "modian_col_invoice_number": {"fa": "شماره فاکتور", "en": "Invoice Number", "fr": "Numéro de facture", "de": "Rechnungsnummer"},
    "modian_col_total": {"fa": "مبلغ کل", "en": "Total Amount", "fr": "Montant total", "de": "Gesamtbetrag"},
    "modian_col_status": {"fa": "وضعیت", "en": "Status", "fr": "Statut", "de": "Status"},
    "modian_not_prepared": {"fa": "آماده‌سازی نشده", "en": "Not Prepared", "fr": "Non préparé", "de": "Nicht vorbereitet"},
    "modian_prepare_btn": {"fa": "آماده‌سازی", "en": "Prepare", "fr": "Préparer", "de": "Vorbereiten"},
    "modian_preview_placeholder": {
        "fa": "پیش‌نمایش ساختار JSON آماده‌شده برای ارسال اینجا نمایش داده می‌شود...",
        "en": "The prepared JSON structure ready for submission will be shown here...",
        "fr": "La structure JSON préparée pour l'envoi sera affichée ici...",
        "de": "Die vorbereitete JSON-Struktur für die Übermittlung wird hier angezeigt...",
    },
    "modian_ready_title": {"fa": "آماده شد", "en": "Ready", "fr": "Prêt", "de": "Bereit"},
    "modian_ready_message": {
        "fa": "ساختار داده صورتحساب آماده شد. برای ارسال واقعی به سامانه مودیان، نیاز به تنظیم گواهی دیجیتال و اتصال API واقعی است.",
        "en": "The invoice data structure is ready. Sending it for real to the Modian system requires a digital certificate and a real API connection.",
        "fr": "La structure de données de la facture est prête. L'envoi réel au système fiscal nécessite un certificat numérique et une connexion API réelle.",
        "de": "Die Rechnungsdatenstruktur ist bereit. Der tatsächliche Versand an das Modian-System erfordert ein digitales Zertifikat und eine echte API-Verbindung.",
    },
    "modian_error_prepare": {"fa": "خطا در آماده‌سازی سند:\n{error}", "en": "Error preparing document:\n{error}", "fr": "Erreur lors de la préparation du document :\n{error}", "de": "Fehler bei der Dokumentvorbereitung:\n{error}"},
    "modian_saved_title": {"fa": "ذخیره شد", "en": "Saved", "fr": "Enregistré", "de": "Gespeichert"},
    "modian_saved_message": {
        "fa": "تنظیمات اتصال ذخیره شد. توجه: این تنظیمات فقط ذخیره می‌شوند؛ اتصال واقعی به سامانه مودیان همچنان نیازمند تکمیل send_to_modian() توسط توسعه‌دهنده است.",
        "en": "Connection settings saved. Note: these settings are only stored; a real connection to the Modian system still requires the developer to complete send_to_modian().",
        "fr": "Paramètres de connexion enregistrés. Remarque : ces paramètres sont uniquement stockés ; une connexion réelle au système fiscal nécessite toujours que le développeur complète send_to_modian().",
        "de": "Verbindungseinstellungen gespeichert. Hinweis: Diese Einstellungen werden nur gespeichert; eine echte Verbindung zum Modian-System erfordert weiterhin, dass der Entwickler send_to_modian() fertigstellt.",
    },
    "modian_error_save": {"fa": "خطا در ذخیره تنظیمات:\n{error}", "en": "Error saving settings:\n{error}", "fr": "Erreur lors de l'enregistrement des paramètres :\n{error}", "de": "Fehler beim Speichern der Einstellungen:\n{error}"},

    # ---------------- تنظیمات ----------------
    "settings_page_title": {"fa": "تنظیمات سیستم", "en": "System Settings", "fr": "Paramètres système", "de": "Systemeinstellungen"},
    "settings_access_denied": {
        "fa": "دسترسی به این بخش فقط برای مدیر سیستم مجاز است.", "en": "Access to this section is only allowed for the system administrator.",
        "fr": "L'accès à cette section est réservé à l'administrateur système.", "de": "Der Zugriff auf diesen Bereich ist nur dem Systemadministrator erlaubt.",
    },
    "settings_tab_users": {"fa": "مدیریت کاربران", "en": "User Management", "fr": "Gestion des utilisateurs", "de": "Benutzerverwaltung"},
    "settings_tab_boxes": {"fa": "مدیریت صندوق‌ها", "en": "Register Management", "fr": "Gestion des caisses", "de": "Kassenverwaltung"},
    "settings_tab_scanner": {"fa": "بارکدخوان", "en": "Barcode Scanner", "fr": "Lecteur de code-barres", "de": "Barcode-Scanner"},
    "settings_tab_sms": {"fa": "پیامک", "en": "SMS", "fr": "SMS", "de": "SMS"},

    "settings_username_label": {"fa": "نام کاربری:", "en": "Username:", "fr": "Nom d'utilisateur :", "de": "Benutzername:"},
    "settings_password_label": {"fa": "رمز عبور:", "en": "Password:", "fr": "Mot de passe :", "de": "Passwort:"},
    "settings_fullname_label": {"fa": "نام کامل:", "en": "Full Name:", "fr": "Nom complet :", "de": "Vollständiger Name:"},
    "settings_role_label": {"fa": "نقش:", "en": "Role:", "fr": "Rôle :", "de": "Rolle:"},
    "settings_role_cashier": {"fa": "صندوق‌دار", "en": "Cashier", "fr": "Caissier", "de": "Kassierer"},
    "settings_role_accountant": {"fa": "حسابدار", "en": "Accountant", "fr": "Comptable", "de": "Buchhalter"},
    "settings_role_admin": {"fa": "مدیر فروشگاه (ادمین)", "en": "Store Manager (Admin)", "fr": "Gérant du magasin (Admin)", "de": "Filialleiter (Admin)"},
    "settings_box_label": {"fa": "صندوق تخصیصی:", "en": "Assigned Register:", "fr": "Caisse assignée :", "de": "Zugewiesene Kasse:"},
    "settings_create_user_btn": {"fa": "+ ایجاد کاربر جدید", "en": "+ Create New User", "fr": "+ Créer un nouvel utilisateur", "de": "+ Neuen Benutzer erstellen"},
    "settings_edit_user_btn": {"fa": "ویرایش اطلاعات کاربر", "en": "Edit User Info", "fr": "Modifier les infos utilisateur", "de": "Benutzerinfo bearbeiten"},
    "settings_change_password_btn": {"fa": "تغییر رمز عبور", "en": "Change Password", "fr": "Changer le mot de passe", "de": "Passwort ändern"},
    "settings_toggle_active_btn": {"fa": "فعال/غیرفعال کردن کاربر", "en": "Activate/Deactivate User", "fr": "Activer/Désactiver l'utilisateur", "de": "Benutzer aktivieren/deaktivieren"},
    "settings_col_id": {"fa": "شناسه", "en": "ID", "fr": "ID", "de": "ID"},
    "settings_col_username": {"fa": "نام کاربری", "en": "Username", "fr": "Nom d'utilisateur", "de": "Benutzername"},
    "settings_col_fullname": {"fa": "نام کامل", "en": "Full Name", "fr": "Nom complet", "de": "Vollständiger Name"},
    "settings_col_role": {"fa": "نقش", "en": "Role", "fr": "Rôle", "de": "Rolle"},
    "settings_col_box": {"fa": "صندوق", "en": "Register", "fr": "Caisse", "de": "Kasse"},
    "settings_col_status": {"fa": "وضعیت", "en": "Status", "fr": "Statut", "de": "Status"},
    "settings_status_active": {"fa": "فعال", "en": "Active", "fr": "Actif", "de": "Aktiv"},
    "settings_status_inactive": {"fa": "غیرفعال", "en": "Inactive", "fr": "Inactif", "de": "Inaktiv"},
    "settings_error_all_fields": {"fa": "تمام فیلدها الزامی هستند.", "en": "All fields are required.", "fr": "Tous les champs sont obligatoires.", "de": "Alle Felder sind erforderlich."},
    "settings_user_created": {"fa": "کاربر جدید با موفقیت ایجاد شد.", "en": "New user created successfully.", "fr": "Nouvel utilisateur créé avec succès.", "de": "Neuer Benutzer erfolgreich erstellt."},
    "settings_error_create_user": {
        "fa": "خطا در ایجاد کاربر (احتمالاً نام کاربری تکراری است):\n{error}",
        "en": "Error creating user (username is probably duplicated):\n{error}",
        "fr": "Erreur lors de la création de l'utilisateur (le nom d'utilisateur est probablement en double) :\n{error}",
        "de": "Fehler beim Erstellen des Benutzers (Benutzername wahrscheinlich doppelt):\n{error}",
    },
    "settings_select_user_first": {"fa": "لطفاً ابتدا یک کاربر را از لیست انتخاب کنید.", "en": "Please select a user from the list first.", "fr": "Veuillez d'abord sélectionner un utilisateur dans la liste.", "de": "Bitte zuerst einen Benutzer aus der Liste auswählen."},
    "settings_edit_user_dialog_title": {"fa": "ویرایش کاربر", "en": "Edit User", "fr": "Modifier l'utilisateur", "de": "Benutzer bearbeiten"},
    "settings_change_password_dialog_title": {"fa": "تغییر رمز عبور", "en": "Change Password", "fr": "Changer le mot de passe", "de": "Passwort ändern"},
    "settings_new_password_label": {"fa": "رمز عبور جدید:", "en": "New Password:", "fr": "Nouveau mot de passe :", "de": "Neues Passwort:"},
    "settings_error_empty_password": {"fa": "رمز عبور نمی‌تواند خالی باشد.", "en": "Password cannot be empty.", "fr": "Le mot de passe ne peut pas être vide.", "de": "Passwort darf nicht leer sein."},
    "settings_password_changed": {"fa": "رمز عبور با موفقیت تغییر کرد.", "en": "Password changed successfully.", "fr": "Mot de passe changé avec succès.", "de": "Passwort erfolgreich geändert."},
    "settings_confirm_toggle": {"fa": "آیا از {action}‌کردن کاربر «{name}» اطمینان دارید؟", "en": "Are you sure you want to {action} user \"{name}\"?", "fr": "Voulez-vous vraiment {action} l'utilisateur « {name} » ?", "de": "Möchten Sie den Benutzer „{name}“ wirklich {action}?"},
    "settings_action_activate": {"fa": "فعال", "en": "activate", "fr": "activer", "de": "aktivieren"},
    "settings_action_deactivate": {"fa": "غیرفعال", "en": "deactivate", "fr": "désactiver", "de": "deaktivieren"},

    "settings_new_box_placeholder": {"fa": "نام صندوق جدید...", "en": "New register name...", "fr": "Nom de la nouvelle caisse...", "de": "Neuer Kassenname..."},
    "settings_add_box_btn": {"fa": "+ افزودن صندوق", "en": "+ Add Register", "fr": "+ Ajouter une caisse", "de": "+ Kasse hinzufügen"},
    "settings_col_box_name": {"fa": "نام صندوق", "en": "Register Name", "fr": "Nom de la caisse", "de": "Kassenname"},
    "settings_error_add_box": {"fa": "خطا در افزودن صندوق:\n{error}", "en": "Error adding register:\n{error}", "fr": "Erreur lors de l'ajout de la caisse :\n{error}", "de": "Fehler beim Hinzufügen der Kasse:\n{error}"},

    "settings_scanner_note": {
        "fa": "برای بارکدخوان‌های USB که مثل کیبورد عمل می‌کنند (اکثر مدل‌های بازار)، نیازی به هیچ تنظیمی نیست؛ فقط کافی است نوع اتصال روی «USB» بماند. فقط برای بارکدخوان‌های سریال (پورت COM) لازم است پورت و Baud Rate را وارد کنید.",
        "en": "USB barcode scanners that act like a keyboard (most models on the market) need no configuration; just keep the connection type set to \"USB\". Only serial (COM port) scanners require entering the port and baud rate.",
        "fr": "Les lecteurs de code-barres USB qui agissent comme un clavier (la plupart des modèles du marché) ne nécessitent aucune configuration ; laissez simplement le type de connexion sur « USB ». Seuls les lecteurs série (port COM) nécessitent la saisie du port et du débit en bauds.",
        "de": "USB-Barcode-Scanner, die wie eine Tastatur funktionieren (die meisten Marktmodelle), benötigen keine Konfiguration; lassen Sie den Verbindungstyp einfach auf „USB“. Nur serielle (COM-Port) Scanner erfordern die Eingabe von Port und Baudrate.",
    },
    "settings_pyserial_warning": {
        "fa": "⚠️ کتابخانه pyserial نصب نیست. برای استفاده از حالت سریال، دستور 'pip install pyserial' را اجرا کنید.",
        "en": "⚠️ The pyserial library is not installed. To use serial mode, run 'pip install pyserial'.",
        "fr": "⚠️ La bibliothèque pyserial n'est pas installée. Pour utiliser le mode série, exécutez 'pip install pyserial'.",
        "de": "⚠️ Die pyserial-Bibliothek ist nicht installiert. Für den seriellen Modus 'pip install pyserial' ausführen.",
    },
    "settings_scanner_mode_usb": {"fa": "USB (کیبوردی) - پیش‌فرض", "en": "USB (Keyboard) - Default", "fr": "USB (clavier) - Par défaut", "de": "USB (Tastatur) - Standard"},
    "settings_scanner_mode_serial": {"fa": "سریال (پورت COM)", "en": "Serial (COM Port)", "fr": "Série (port COM)", "de": "Seriell (COM-Port)"},
    "settings_connection_type_label": {"fa": "نوع اتصال:", "en": "Connection Type:", "fr": "Type de connexion :", "de": "Verbindungstyp:"},
    "settings_serial_port_label": {"fa": "پورت سریال:", "en": "Serial Port:", "fr": "Port série :", "de": "Serieller Port:"},
    "settings_serial_port_placeholder": {
        "fa": "مثلاً COM3 (ویندوز) یا /dev/ttyUSB0 (لینوکس)", "en": "e.g. COM3 (Windows) or /dev/ttyUSB0 (Linux)",
        "fr": "ex. COM3 (Windows) ou /dev/ttyUSB0 (Linux)", "de": "z. B. COM3 (Windows) oder /dev/ttyUSB0 (Linux)",
    },
    "settings_baud_rate_label": {"fa": "Baud Rate:", "en": "Baud Rate:", "fr": "Débit en bauds :", "de": "Baudrate:"},
    "settings_save_settings_btn": {"fa": "ذخیره تنظیمات", "en": "Save Settings", "fr": "Enregistrer les paramètres", "de": "Einstellungen speichern"},
    "settings_restart_hint": {
        "fa": "پس از ذخیره، برای اعمال کامل تغییرات، برنامه را مجدداً اجرا کنید.", "en": "After saving, restart the app for the changes to take full effect.",
        "fr": "Après l'enregistrement, redémarrez l'application pour appliquer complètement les changements.", "de": "Nach dem Speichern die App neu starten, damit die Änderungen vollständig wirksam werden.",
    },
    "settings_scanner_saved_message": {
        "fa": "تنظیمات بارکدخوان ذخیره شد. برای اعمال کامل، برنامه را مجدداً اجرا کنید.",
        "en": "Scanner settings saved. Restart the app for full effect.",
        "fr": "Paramètres du lecteur enregistrés. Redémarrez l'application pour un effet complet.",
        "de": "Scanner-Einstellungen gespeichert. App für volle Wirkung neu starten.",
    },

    "settings_sms_note": {
        "fa": "این تنظیمات برای اتصال به یک سرویس‌دهنده‌ی پیامک واقعی لازم است. تا زمانی که تنظیمات لازم (API Key یا آدرس API) وارد نشود، پیامک‌ها فقط در سیستم ثبت می‌شوند و واقعاً ارسال نمی‌شوند.",
        "en": "These settings are needed to connect to a real SMS provider. Until the required settings (API Key or API URL) are entered, messages are only recorded in the system and not actually sent.",
        "fr": "Ces paramètres sont nécessaires pour se connecter à un véritable fournisseur de SMS. Tant que les paramètres requis (clé API ou URL API) ne sont pas saisis, les messages sont uniquement enregistrés dans le système et non réellement envoyés.",
        "de": "Diese Einstellungen sind für die Verbindung zu einem echten SMS-Anbieter erforderlich. Bis die erforderlichen Einstellungen (API-Schlüssel oder API-URL) eingegeben sind, werden Nachrichten nur im System erfasst und nicht tatsächlich gesendet.",
    },
    "settings_provider_kavenegar": {"fa": "کاوه‌نگار", "en": "Kavenegar", "fr": "Kavenegar", "de": "Kavenegar"},
    "settings_provider_melipayamak": {"fa": "ملی‌پیامک", "en": "Melipayamak", "fr": "Melipayamak", "de": "Melipayamak"},
    "settings_provider_generic": {"fa": "سایر (HTTP عمومی)", "en": "Other (Generic HTTP)", "fr": "Autre (HTTP générique)", "de": "Andere (Generisches HTTP)"},
    "settings_provider_label": {"fa": "سرویس‌دهنده:", "en": "Provider:", "fr": "Fournisseur :", "de": "Anbieter:"},
    "settings_api_key_label": {"fa": "API Key:", "en": "API Key:", "fr": "Clé API :", "de": "API-Schlüssel:"},
    "settings_api_key_placeholder": {"fa": "برای ملی‌پیامک: نام کاربری پنل", "en": "For Melipayamak: panel username", "fr": "Pour Melipayamak : nom d'utilisateur du panneau", "de": "Für Melipayamak: Panel-Benutzername"},
    "settings_api_url_label": {"fa": "آدرس API:", "en": "API URL:", "fr": "URL de l'API :", "de": "API-URL:"},
    "settings_api_url_placeholder": {
        "fa": "برای ملی‌پیامک: رمز عبور پنل  |  برای HTTP عمومی: آدرس کامل API",
        "en": "For Melipayamak: panel password  |  For generic HTTP: full API URL",
        "fr": "Pour Melipayamak : mot de passe du panneau  |  Pour HTTP générique : URL complète de l'API",
        "de": "Für Melipayamak: Panel-Passwort  |  Für generisches HTTP: vollständige API-URL",
    },
    "settings_sender_label": {"fa": "شماره فرستنده:", "en": "Sender Number:", "fr": "Numéro d'expéditeur :", "de": "Absendernummer:"},
    "settings_sender_placeholder": {"fa": "مثلاً 30007xxxxx", "en": "e.g. 30007xxxxx", "fr": "ex. 30007xxxxx", "de": "z. B. 30007xxxxx"},
    "settings_http_method_label": {"fa": "روش HTTP (فقط برای «سایر»):", "en": "HTTP Method (only for \"Other\"):", "fr": "Méthode HTTP (uniquement pour « Autre ») :", "de": "HTTP-Methode (nur für „Andere“):"},
    "settings_payload_template_label": {"fa": "قالب پیام JSON (فقط برای «سایر»):", "en": "JSON Payload Template (only for \"Other\"):", "fr": "Modèle de charge utile JSON (uniquement pour « Autre ») :", "de": "JSON-Payload-Vorlage (nur für „Andere“):"},
    "settings_payload_hint": {
        "fa": "در قالب پیام می‌توانید از {phone}، {message}، {sender} و {api_key} به‌عنوان جای‌گزین استفاده کنید؛ اگر خالی بماند، یک قالب پیش‌فرض استفاده می‌شود.",
        "en": "In the payload template, you can use {phone}, {message}, {sender}, and {api_key} as placeholders; a default template is used if left empty.",
        "fr": "Dans le modèle de charge utile, vous pouvez utiliser {phone}, {message}, {sender} et {api_key} comme espaces réservés ; un modèle par défaut est utilisé s'il est laissé vide.",
        "de": "In der Payload-Vorlage können Sie {phone}, {message}, {sender} und {api_key} als Platzhalter verwenden; wenn leer, wird eine Standardvorlage verwendet.",
    },
    "settings_sms_saved_message": {"fa": "تنظیمات سرویس پیامک ذخیره شد.", "en": "SMS provider settings saved.", "fr": "Paramètres du fournisseur SMS enregistrés.", "de": "SMS-Anbietereinstellungen gespeichert."},

    # ---------------- پنجره رسید فاکتور ----------------
    "receipt_invoice_number_label": {"fa": "شماره فاکتور: {number}", "en": "Invoice Number: {number}", "fr": "Numéro de facture : {number}", "de": "Rechnungsnummer: {number}"},
    "receipt_col_name": {"fa": "نام کالا", "en": "Item Name", "fr": "Nom de l'article", "de": "Artikelname"},
    "receipt_col_qty": {"fa": "تعداد", "en": "Qty", "fr": "Quantité", "de": "Menge"},
    "receipt_col_price": {"fa": "قیمت واحد", "en": "Unit Price", "fr": "Prix unitaire", "de": "Einzelpreis"},
    "receipt_total_label": {"fa": "مبلغ نهایی: {amount} ریال", "en": "Final Amount: {amount}", "fr": "Montant final : {amount}", "de": "Endbetrag: {amount}"},
    "receipt_print_btn": {"fa": "چاپ فاکتور", "en": "Print Invoice", "fr": "Imprimer la facture", "de": "Rechnung drucken"},

    # ---------------- درباره ----------------
    "menu_about": {"fa": "درباره", "en": "About", "fr": "À propos", "de": "Über"},
    "about_page_title": {"fa": "درباره‌ی برنامه", "en": "About the Application", "fr": "À propos de l'application", "de": "Über die Anwendung"},
    "about_app_description": {
        "fa": "نرم‌افزار یکپارچه حسابداری، فروش، خرید و انبارداری با پشتیبانی از چند صندوق و چند زبان.",
        "en": "Integrated accounting, sales, purchasing and inventory software with multi-register and multi-language support.",
        "fr": "Logiciel intégré de comptabilité, vente, achat et inventaire avec prise en charge de plusieurs caisses et langues.",
        "de": "Integrierte Software für Buchhaltung, Verkauf, Einkauf und Lager mit Unterstützung für mehrere Kassen und Sprachen.",
    },
    "about_contact_title": {"fa": "اطلاعات تماس سازنده", "en": "Developer Contact Information", "fr": "Coordonnées du développeur", "de": "Kontaktdaten des Entwicklers"},
    "about_developer_label": {"fa": "سازنده:", "en": "Developer:", "fr": "Développeur :", "de": "Entwickler:"},
    "about_email_label": {"fa": "ایمیل:", "en": "Email:", "fr": "E-mail :", "de": "E-Mail:"},
    "about_whatsapp_label": {"fa": "واتساپ:", "en": "WhatsApp:", "fr": "WhatsApp :", "de": "WhatsApp:"},
    "about_contact_hint": {
        "fa": "برای پشتیبانی، پیشنهاد یا گزارش مشکل با من در تماس باشید.",
        "en": "Feel free to contact me for support, suggestions, or to report an issue.",
        "fr": "N'hésitez pas à me contacter pour du support, des suggestions ou pour signaler un problème.",
        "de": "Kontaktieren Sie mich gerne für Support, Vorschläge oder um ein Problem zu melden.",
    },
}


def set_language(lang_code: str):
    """تغییر زبان جاری برنامه؛ باید کد یکی از SUPPORTED_LANGUAGES باشد."""
    global _current_language
    if lang_code in SUPPORTED_LANGUAGES:
        _current_language = lang_code


def get_language() -> str:
    return _current_language


def get_layout_direction():
    """
    تبدیل جهت متن زبان جاری ("rtl"/"ltr") به Qt.LayoutDirection.
    import پی‌کیوتی اینجا (محلی) انجام می‌شود تا خودِ این ماژول بدون PyQt6 هم
    قابل import و تست باشد (مثلاً در اسکریپت‌های تست خط‌فرمان).
    """
    from PyQt6.QtCore import Qt
    direction_str = SUPPORTED_LANGUAGES[_current_language]["direction"]
    return Qt.LayoutDirection.RightToLeft if direction_str == "rtl" else Qt.LayoutDirection.LeftToRight


def tr(key: str, **kwargs) -> str:
    """
    برگرداندن ترجمه‌ی کلید در زبان جاری. اگر کلید یا ترجمه‌اش برای زبان جاری
    پیدا نشود، به فارسی (زبان مرجع) برمی‌گردد و در نهایت خودِ کلید را نشان
    می‌دهد تا هیچ‌وقت متن خالی دیده نشود.
    kwargs برای جای‌گزین‌های داخل متن استفاده می‌شود، مثل tr("dashboard_welcome", name="رستین").
    """
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(_current_language) or entry.get("fa") or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
