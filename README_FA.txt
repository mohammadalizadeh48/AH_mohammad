راهنمای اجرای سایت

۱) Python 3.10+ نصب کن.
۲) در پوشه پروژه اجرا کن: pip install -r requirements.txt
۳) در PowerShell رمز مدیر را تنظیم کن: $env:ADMIN_PASSWORD="یک-رمز-قوی-و-شخصی"
۴) اجرا: python app.py
۵) سایت: http://127.0.0.1:3000
۶) پنل مدیریت: http://127.0.0.1:3000/admin

پنل بدون متغیر ADMIN_PASSWORD فعال نمی‌شود. برای انتشار عمومی HTTPS و کلید FLASK_SECRET_KEY قوی تنظیم کن؛ از سرور توسعه Flask برای میزبانی عمومی استفاده نکن.
