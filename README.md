# آماده‌سازی مصاحبه بک‌اند — پروژه «CloudLab»

پروژه تمرینی: یک سرویس مدیریت منابع ابری (VM) با Django 5.2 LTS + MySQL 8.

## راه‌اندازی
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
# MySQL: دیتابیس و کاربر cloudlab (رمز: cloudlab) را بسازید؛ متغیرهای DB_* قابل تنظیم‌اند
python manage.py migrate
python manage.py test
```

## درس‌ها
| # | موضوع | دسته |
|---|-------|------|
| 1 | [معماری و کد تمیز در Django](docs/lessons/01-architecture.md) | عمیق |
| 2 | پایگاه داده و طراحی اسکیما | مهم |
| 3 | احراز هویت | مهم |
| 4 | Caching با Redis | مهم |
| 5 | Sync/Async، Celery و RabbitMQ | مهم |
| 6 | Design patternها | عمیق |
| 7 | ساختمان داده برای طراحی سیستم | مهم |
| 8 | System design | عمیق |
| 9 | Docker و مفاهیم ابری | توضیحی |
