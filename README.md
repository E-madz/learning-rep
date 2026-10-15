# آماده‌سازی مصاحبه بک‌اند — پروژه «CloudLab»

پروژه تمرینی: یک سرویس مدیریت منابع ابری (VM) با Django 5.2 LTS + MySQL 8.

## ساختار
```
backend/    پروژه Django (manage.py, config/, apps/)
docs/       درس‌ها (فارسی)
docker/     فایل‌های کمکی دیتابیس لوکال
docker-compose.yml   فقط MySQL برای توسعه لوکال
```

## اجرا روی لوکال

### پیش‌نیازها
- Python 3.12 یا بالاتر
- Docker (برای MySQL) — یا یک MySQL 8 نصب‌شده روی سیستم
- کتابخانه‌های build برای `mysqlclient`:
  - Ubuntu/Debian: `sudo apt install build-essential pkg-config python3-dev libmysqlclient-dev`
  - macOS: `brew install mysql pkg-config`
  - Windows: معمولاً wheel آماده نصب می‌شود؛ اگر نشد، WSL2 با Ubuntu را پیشنهاد می‌کنم

### مراحل
```bash
git clone <repo-url> && cd learning-rep
git checkout claude/dazzling-brown-819exj

# 1) دیتابیس
docker compose up -d db          # منتظر healthy شدن بمانید: docker compose ps

# 2) محیط پایتون
cd backend
python3 -m venv .venv && source .venv/bin/activate    # ویندوز: .venv\Scripts\activate
pip install -r requirements.txt

# 3) migration و اجرا
python manage.py migrate
python manage.py createsuperuser  # برای ورود به admin و تست API
python manage.py runserver        # http://127.0.0.1:8000
```

### تست
```bash
python manage.py test
```

### خطای `port 3306 already in use`
یعنی روی سیستم شما یک MySQL دیگر روی پورت 3306 در حال اجراست. یکی از دو راه:
```bash
# راه ۱: دیتابیس Docker را روی پورت دیگری بالا بیاورید
docker compose down
export DB_PORT=3307              # در همان ترمینالی که docker compose و Django را اجرا می‌کنید
docker compose up -d db
# و Django هم از همین متغیر محیطی استفاده می‌کند (همان ترمینال)

# راه ۲: MySQL لوکال را متوقف کنید (اگر لازمش ندارید)
sudo systemctl stop mysql
```
برای دیدن اینکه چه چیزی پورت را گرفته: `sudo ss -ltnp | grep 3306`

### امتحان سریع API
بعد از `createsuperuser`، با session (مرورگر) یا BasicAuth:
```bash
curl -u USER:PASS -X POST http://127.0.0.1:8000/api/vms/ \
  -H "Content-Type: application/json" \
  -d '{"name":"web-1","cpu":2,"ram_mb":2048}'
curl -u USER:PASS http://127.0.0.1:8000/api/vms/
curl -u USER:PASS -X POST http://127.0.0.1:8000/api/vms/1/start/
curl -u USER:PASS -X DELETE http://127.0.0.1:8000/api/vms/1/
```
(احراز هویت درست‌وحسابی را در درس ۳ می‌سازیم؛ فعلاً BasicAuth پیش‌فرض DRF کافی است.)

### بدون Docker (MySQL لوکال)
در MySQL خودتان (در اوبونتو معمولاً `sudo mysql`) این را اجرا کنید:
```sql
CREATE DATABASE cloudlab CHARACTER SET utf8mb4;
CREATE USER 'cloudlab'@'localhost' IDENTIFIED BY 'cloudlab';
GRANT ALL ON cloudlab.* TO 'cloudlab'@'localhost';
GRANT ALL ON `test\_cloudlab`.* TO 'cloudlab'@'localhost';  -- دیتابیس موقت تست‌های جنگو
FLUSH PRIVILEGES;
```
کاربر `cloudlab` فقط به همین دو دیتابیس دسترسی دارد. بقیه دیتابیس‌های شما دست‌نخورده می‌مانند.
اگر پورت یا رمز شما فرق دارد، با متغیرهای محیطی `DB_*` عوض کنید (نمونه: `backend/.env.example`).

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
