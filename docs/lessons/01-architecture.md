# درس ۱: معماری و کد تمیز در Django

## هدف
بتوانید در مصاحبه توضیح بدهید **چرا** کد را لایه‌بندی می‌کنیم و این لایه‌ها در یک پروژه Django چه شکلی‌اند.

## ۱. مشکل: «Fat Views / Fat Models»
در پروژه‌های ساده، منطق کسب‌وکار (مثل چک کردن quota) داخل view یا serializer نوشته می‌شود. مشکلاتش:
- تست کردن سخت است (باید request فرضی بسازید).
- همان منطق در جای دیگر (مثلاً Celery task یا management command) تکرار می‌شود.
- تغییر یک قانون، چند فایل را تحت تأثیر می‌گذارد.

## ۲. لایه‌ها در این پروژه
```
HTTP request
   │
   ▼
api/views.py        → فقط: گرفتن ورودی، صدا زدن service، تبدیل خطا به HTTP status
api/serializers.py  → فقط: validation ورودی/خروجی (شکل داده، نه قانون کسب‌وکار)
   │
   ▼
services.py         → قوانین کسب‌وکار (quota، state machine، transaction)
   │
   ▼
repositories.py     → دسترسی به داده (ORM query ها)
   │
   ▼
models.py           → ساختار جداول
```
قانون اصلی: **وابستگی فقط به سمت پایین**. service نمی‌داند HTTP چیست؛ view نمی‌داند ORM query چطور نوشته می‌شود.

## ۳. اصول کلیدی (سؤال‌های رایج مصاحبه)

**Separation of Concerns / Single Responsibility (S در SOLID)**
هر کلاس/ماژول یک دلیل برای تغییر دارد. view تغییر می‌کند اگر فرمت API عوض شود؛ service اگر قانون عوض شود.

**Dependency Injection (D در SOLID)**
`VirtualMachineService.__init__(repo=None)` — repository را از بیرون می‌گیرد. در تست می‌توان repository جعلی داد، و اگر فردا دیتابیس عوض شد، service تغییر نمی‌کند.

**Domain Exceptions**
service خطاهای دامنه‌ای (`QuotaExceeded`) می‌اندازد، نه `HTTP 403`. view آن‌ها را به status code ترجمه می‌کند (جدول `ERROR_STATUS`). نتیجه: همان service در Celery task هم قابل استفاده است.

**State Machine**
`ALLOWED_TRANSITIONS` یک دیکشنری ساده است که مشخص می‌کند از هر وضعیت به کدام وضعیت‌ها می‌شود رفت. به‌جای `if` های پراکنده، قانون در یک جا و قابل‌خواندن است.

**Transaction + `select_for_update`**
در `_transition`، ردیف را lock می‌کنیم تا دو درخواست همزمان (مثلاً دو بار `start`) هر دو موفق نشوند. بدون lock: *race condition*.

## ۴. چه چیزی را عمداً ساده نگه داشتیم (و در مصاحبه می‌توانید بگویید)
- **Repository روی Django ORM** گاهی over-engineering است، چون ORM خودش یک abstraction است. دلیل وجودش اینجا: تمرین جدا کردن لایه‌ها و راحتی mock. در پروژه کوچک می‌شود از `Model.objects` مستقیم در service استفاده کرد؛ مهم این است که **تصمیم آگاهانه** باشد.
- **چک یکتا بودن نام** در service race-free نیست، چون MySQL از unique index شرطی پشتیبانی نمی‌کند (Django هشدار `W036` می‌دهد). راه‌حل‌ها (generated column، ستون `active_key` nullable) را در درس دیتابیس می‌بینیم.

## ۵. سؤال‌های مصاحبه برای خودآزمایی
1. چرا منطق کسب‌وکار را داخل view نمی‌گذاریم؟
2. تفاوت serializer validation و business rule چیست؟ (مثال: `cpu ≤ 16` اعتبارسنجی است؛ quota هر کاربر قانون کسب‌وکار.)
3. `select_for_update` چه مشکلی را حل می‌کند؟ چه زمانی کار نمی‌کند؟ (خارج از transaction.)
4. Dependency Injection چه کمکی به تست می‌کند؟
5. Repository pattern روی ORM چه مزیت و چه هزینه‌ای دارد؟
6. چرا خطا را در service به `403` تبدیل نمی‌کنیم؟

## ۶. تمرین (برای خودتان)
1. endpoint جدید «تغییر اندازه VM» (`resize`) اضافه کنید: فقط وقتی VM در وضعیت `stopped` است، و quota را دوباره چک کند. قانون را در **service** بنویسید، نه view.
2. یک تست بنویسید که service را با یک `FakeRepository` (بدون دیتابیس) اجرا کند.

## کد مربوط
- `backend/apps/compute/models.py`, `repositories.py`, `services.py`, `exceptions.py`
- `backend/apps/compute/api/` , `backend/apps/compute/tests/`
