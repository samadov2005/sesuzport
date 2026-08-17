# 🛡️ SESPORT — Iste'molchilarni Himoya Qilish Platformasi

> **Telegram bot + Django admin panel** orqali muddati o'tgan va sifatsiz mahsulotlar haqida shikoyat qabul qilish, ko'rib chiqish va hal qilish tizimi.

---

## 📋 Mundarija

- [Loyiha haqida](#-loyiha-haqida)
- [Texnologiyalar](#-texnologiyalar)
- [Arxitektura](#-arxitektura)
- [Loyiha tuzilmasi](#-loyiha-tuzilmasi)
- [O'rnatish va ishga tushirish](#-o'rnatish-va-ishga-tushirish)
- [Seed tizimi](#-seed-tizimi)
- [Telegram Bot — Qo'llanma](#-telegram-bot--qollanma)
- [Django Admin Panel](#-django-admin-panel)
- [Ma'lumotlar bazasi modellari](#-malumotlar-bazasi-modellari)
- [Bot holat mashinalari (FSM)](#-bot-holat-mashinalari-fsm)
- [Xabardorlik tizimi](#-xabardorlik-tizimi)
- [Konfiguratsiya (.env)](#-konfiguratsiya-env)
- [Docker bilan ishga tushirish](#-docker-bilan-ishga-tushirish)
- [Loyihani kengaytirish](#-loyihani-kengaytirish)

---

## 📌 Loyiha haqida

**SESPORT** — O'zbekiston iste'molchilarini sifatsiz va muddati o'tgan mahsulotlardan himoya qilish uchun yaratilgan platforma.

### Asosiy funksiyalar:

| Funksiya | Tavsif |
|----------|--------|
| 📝 Shikoyat yuborish | Foydalanuvchi tavsif + rasm + GPS orqali murojaat yuboradi |
| 🎫 Ticket ID | Har bir murojaat `SES-2026-000001` formatida noyob ID oladi |
| 🔍 Moderatsiya | Admin panel orqali murojaatni ko'rib chiqish va holat o'zgartirish |
| 📱 Telegram xabardorlik | Holat o'zgarganda foydalanuvchiga bot orqali xabar ketadi |
| 🏪 Do'konlar reytingi | Do'konlarning xavfsizlik holati (🟢🟡🔴) va GPS orqali yaqin do'konlar |
| 💳 Keshbek tizimi | Foydalanuvchi murojaatlari uchun bonus oladi |
| ⚖️ Iste'molchi huquqlari | O'zbekiston qonunchiligiga asoslangan ma'lumotlar |
| 💬 Yordam | Admin kontakt ma'lumotlari |

---

## 🛠 Texnologiyalar

| Qatlam | Texnologiya | Versiya |
|--------|-------------|---------|
| **Backend** | Python | 3.11+ |
| **Web Framework** | Django | 5.1.4 |
| **Telegram Bot** | Aiogram | 3.15.0 |
| **Ma'lumotlar bazasi (dev)** | SQLite | — |
| **Ma'lumotlar bazasi (prod)** | PostgreSQL | 15+ |
| **Cache / FSM** | Redis | 5+ |
| **Async ORM bridge** | asgiref (sync_to_async) | 3.7+ |
| **Web server** | Gunicorn + Nginx | — |
| **Konteynerizatsiya** | Docker + Docker Compose | — |
| **Admin UI** | Django Admin (custom dark theme + Chart.js) | — |

---

## 🏗 Arxitektura

```
┌─────────────────────────────────────────────────────┐
│                  FOYDALANUVCHI                      │
│              (Telegram ilovasi)                     │
└────────────────────┬────────────────────────────────┘
                     │ Telegram API
                     ▼
┌─────────────────────────────────────────────────────┐
│              AIOGRAM BOT QATLAMI                    │
│                                                     │
│  bot/main.py          ← Kirish nuqtasi              │
│  bot/middlewares/     ← Auth, throttle, logging     │
│  bot/states/          ← FSM holat mashinalari       │
│  bot/routers/         ← Handler'lar (9 ta router)   │
│  bot/keyboards/       ← Klaviaturalar               │
│  bot/services/        ← Biznes mantiq               │
│  bot/utils/           ← Format yordamchilari        │
└────────────────────┬────────────────────────────────┘
                     │ sync_to_async (ORM calls)
                     ▼
┌─────────────────────────────────────────────────────┐
│             DJANGO BACKEND QATLAMI                  │
│                                                     │
│  apps/users/          ← Telegram foydalanuvchilar  │
│  apps/complaints/     ← Murojaatlar + tarix        │
│  apps/stores/         ← Do'konlar va reyting       │
│  apps/cashback/       ← Keshbek hisoblari          │
│  apps/rights/         ← Iste'molchi huquqlari      │
│  apps/support/        ← Yordam konfiguratsiyasi    │
│                                                     │
│  config/admin.py      ← Premium dashboard          │
│  templates/admin/     ← Dark theme + Chart.js      │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│           MA'LUMOTLAR BAZASI                        │
│  SQLite (dev) / PostgreSQL (prod)                   │
│  Redis (FSM storage — prod)                         │
└─────────────────────────────────────────────────────┘
```

### Muhim arxitektura qarorlari:

1. **Django va Bot — bitta jarayon**: `bot/main.py` birinchi `django.setup()` ni chaqiradi, shundan so'ng ORM ishlaydi
2. **sync_to_async**: Aiogram async, Django ORM sync — `asgiref.sync_to_async` bu ikkalasini bog'laydi
3. **Service qatlami**: Handlerlar to'g'ridan-to'g'ri ORM'ga murojaat qilmaydi — `bot/services/` orqali o'tadi
4. **FSM (Finite State Machine)**: Murojaat yuborish 3 bosqichli: Tavsif → Rasm → GPS

---

## 📁 Loyiha tuzilmasi

```
sesport/
│
├── manage.py                    # Django CLI
├── requirements.txt             # Python kutubxonalar
├── .env                         # Konfiguratsiya (gitda yo'q!)
├── .env.example                 # Namuna konfiguratsiya
├── Dockerfile                   # Docker image (multi-stage, non-root)
├── .dockerignore                # .env / db.sqlite3 / .git image'ga kirmaydi
├── docker-compose.yml           # Servislar: web, bot, db, redis
├── docker-compose.hostport.yml  # Overlay: NPM Docker'da bo'lmasa
├── docker/entrypoint.sh         # DB kutish -> migrate -> collectstatic -> superuser
├── deploy/nginx-standalone/     # ARXIV: NPM'siz variant uchun nginx configlari
├── pytest.ini                   # Test konfiguratsiyasi
├── db.sqlite3                   # SQLite DB (dev) — git'dan chiqarilishi kerak
│
├── config/                      # Django konfiguratsiya
│   ├── settings/
│   │   ├── base.py              # Umumiy sozlamalar
│   │   ├── development.py       # Dev: SQLite, MemoryStorage
│   │   └── production.py        # Prod: PostgreSQL, Redis
│   ├── admin.py                 # Custom AdminSite + dashboard
│   ├── urls.py                  # URL yo'naltirgich
│   ├── wsgi.py                  # WSGI server
│   └── asgi.py                  # ASGI server
│
├── apps/                        # Django ilovalar
│   ├── users/                   # Telegram foydalanuvchilar
│   │   ├── models.py            # TelegramUser modeli
│   │   ├── admin.py             # Admin panel
│   │   ├── migrations/          # DB migratsiyalar
│   │   └── management/
│   │       └── commands/
│   │           ├── seed.py      # Asosiy seed buyrug'i
│   │           ├── seed_real.py # Haqiqiy ma'lumotlar
│   │           └── seed_fake.py # Test ma'lumotlari
│   │
│   ├── complaints/              # Murojaatlar
│   │   ├── models.py            # Complaint, ComplaintStatusHistory
│   │   ├── admin.py             # Status badge, status o'zgartirish
│   │   └── signals.py           # pre_save signal
│   │
│   ├── stores/                  # Do'konlar
│   │   └── models.py            # Store, SafetyStatus
│   │
│   ├── cashback/                # Keshbek
│   │   └── models.py            # CashbackAccount, CashbackTransaction
│   │
│   ├── rights/                  # Iste'molchi huquqlari
│   │   └── models.py            # ConsumerRight
│   │
│   └── support/                 # Yordam
│       └── models.py            # SupportConfiguration
│
├── bot/                         # Telegram bot
│   ├── main.py                  # Bot kirish nuqtasi
│   ├── config.py                # Bot token va sozlamalar
│   │
│   ├── states/                  # FSM holatlari
│   │   ├── complaint.py         # ComplaintStates (3 bosqich)
│   │   └── common.py            # Umumiy holatlar
│   │
│   ├── keyboards/               # Klaviaturalar
│   │   ├── role.py              # Rol tanlash
│   │   ├── consumer.py          # Iste'molchi menyusi
│   │   ├── entrepreneur.py      # Tadbirkor menyusi
│   │   ├── complaint.py         # Murojaat jarayoni
│   │   └── common.py            # Umumiy klaviaturalar
│   │
│   ├── middlewares/             # O'rta qatlamlar
│   │   ├── user_registration.py # Auto ro'yxatdan o'tkazish
│   │   ├── throttling.py        # Anti-spam (1 so'rov/son)
│   │   └── logging_middleware.py# Barcha so'rovlarni log qilish
│   │
│   ├── routers/                 # Handlerlar
│   │   ├── start.py             # /start, /help, /cancel
│   │   ├── consumer.py          # Iste'molchi roli
│   │   ├── entrepreneur.py      # Tadbirkor roli
│   │   ├── complaints.py        # FSM murojaat jarayoni
│   │   ├── stores.py            # Do'kon qidirish
│   │   ├── cashback.py          # Keshbek ko'rish
│   │   ├── rights.py            # Iste'molchi huquqlari
│   │   ├── support.py           # Yordam
│   │   └── common.py            # Noma'lum so'rovlar
│   │
│   ├── services/                # Biznes mantiq (ORM wraps)
│   │   ├── user_service.py      # Foydalanuvchi CRUD
│   │   ├── complaint_service.py # Murojaat CRUD
│   │   ├── store_service.py     # Do'kon qidirish + GPS
│   │   ├── cashback_service.py  # Keshbek hisob-kitob
│   │   └── notification_service.py # Bot xabarlari
│   │
│   ├── filters/
│   │   └── role_filter.py       # Roli bo'yicha filtr
│   │
│   └── utils/
│       └── formatters.py        # Matn formatlash funksiyalar
│
├── templates/                   # Django shablonlar
│   └── admin/
│       ├── base_site.html       # Dark theme CSS
│       └── index.html           # Premium dashboard
│
└── tests/                       # Testlar
    ├── test_users.py
    ├── test_complaints.py
    └── test_cashback.py
```

---

## 🚀 O'rnatish va ishga tushirish

### Talablar:
- Python 3.11+
- pip

### Qadam 1 — Repozitoriyani klonlash

```bash
git clone https://github.com/yourusername/sesport.git
cd sesport
```

### Qadam 2 — Muhit o'zgaruvchilarini sozlash

```bash
# .env.example faylini .env ga nusxalang
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac
```

`.env` faylini oching va quyidagi majburiy qiymatlarni to'ldiring:

```env
BOT_TOKEN=your_bot_token_here        # BotFather dan olingan token
SECRET_KEY=your-django-secret-key    # Ixtiyoriy uzoq string
SEED_MODE=real                        # real yoki fake
```

### Qadam 3 — Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### Qadam 4 — Ma'lumotlar bazasini tayyorlash

```bash
# Migratsiyalarni bajarish (jadvallar yaratiladi)
python manage.py migrate

# Admin foydalanuvchi yaratish
python manage.py createsuperuser
# Username: admin
# Password: xohlagan parol
```

### Qadam 5 — Seed ma'lumotlarini kiritish

```bash
# Real Uzbekiston ma'lumotlari (tavsiya etiladi)
python manage.py seed --mode real

# Yoki test ma'lumotlari (50 user, 100 murojaat)
python manage.py seed --mode fake
```

### Qadam 6 — Servislarni ishga tushirish

**Terminal 1 — Django admin server:**
```bash
python manage.py runserver
# http://127.0.0.1:8000/admin/ da ishlaydi
```

**Terminal 2 — Telegram bot:**
```bash
python -m bot.main
# Bot polling rejimida ishga tushadi
```

---

## 🌱 Seed tizimi

Loyihada ikki xil seed mavjud. `.env` dagi `SEED_MODE` orqali boshqariladi.

### Real seed (`SEED_MODE=real`)

Haqiqiy Uzbekiston ma'lumotlari bilan to'ldiriladi:

| Ma'lumot | Miqdor | Tavsif |
|----------|--------|--------|
| Do'konlar | 10 ta | Korzinka, Makro, Carrefour va boshqalar |
| Murojaatlar | 3 ta | PENDING, UNDER_REVIEW, RESOLVED |
| Foydalanuvchilar | 3 ta | Demo consumer va entrepreneur |
| Iste'molchi huquqlari | 6 ta | O'zbekiston qonunchiligi |
| Yordam config | 1 ta | Telefon, Telegram, email |

### Fake seed (`SEED_MODE=fake`)

Test uchun generatsiya qilingan ma'lumotlar:

| Ma'lumot | Miqdor | Tavsif |
|----------|--------|--------|
| Do'konlar | 30 ta | Toshkent tumanlarida random |
| Foydalanuvchilar | 50 ta | Uzbek ismlar bilan |
| Murojaatlar | 100 ta | Barcha holatlarda |
| Cashback tranzaksiyalar | ~150 ta | Random summalar |

### Buyruqlar:

```bash
# .env dagi SEED_MODE ga qarab ishlaydi
python manage.py seed

# Majburan real
python manage.py seed --mode real

# Majburan fake
python manage.py seed --mode fake

# Avval tozalaydi, keyin seed qiladi
python manage.py seed --mode real --clear
python manage.py seed --mode fake --clear
```

> ⚠️ `--clear` flagi **barcha** murojaatlar, foydalanuvchilar, do'konlar, keshbekni o'chiradi.
> Django admin superuser o'chirilmaydi.

---

## 🤖 Telegram Bot — Qo'llanma

Bot `@sesportuzbot` manziliga yozing yoki o'zingizning tokeningiz bilan ishga tushiring.

### Buyruqlar:

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni boshlash, rol tanlash |
| `/help` | Yordam va buyruqlar ro'yxati |
| `/cancel` | Joriy amalni bekor qilish |

### Rol tanlash:

Botga kirganingizda 2 ta rol taklif etiladi:

- **👤 Iste'molchi (Mijoz)** — shikoyat yuborish, do'konlar, keshbek
- **💼 Tadbirkor** — do'kon statistikasi, reytinglar

### Shikoyat yuborish jarayoni (FSM):

```
/start → 👤 Iste'molchi → 📝 Shikoyat qilish
    │
    ▼ BOSQICH 1
    Mahsulot tavsifini yozing (10-3000 belgi)
    │
    ▼ BOSQICH 2
    Mahsulot rasmini yuboring (foto)
    │
    ▼ BOSQICH 3
    📍 GPS joylashuvini yuboring (tugma orqali)
    │
    ▼
    ✅ Murojaat qabul qilindi!
    🎫 ID: SES-2026-000001
```

> Har qadamda **❌ Bekor qilish** tugmasi mavjud. `/cancel` ham ishlaydi.

### Iste'molchi menyusi:

```
📝 Shikoyat qilish       → Murojaat yuborish (FSM)
📁 Mening murojaatlarim  → Barcha murojaatlarni ko'rish
🏪 Do'konlarni tekshirish → GPS yoki nom bilan qidirish
💳 Keshbeklarni kuzatish  → Balans + oylik + tarix
⚖️ Huquqlarim            → Iste'molchi huquqlari
💬 Yordam                 → Kontakt ma'lumotlari
🔄 Rolni almashtirish    → Boshqa rolga o'tish
```

### Tadbirkor menyusi:

```
🏪 Mening do'konlarim   → Ro'yxatdagi do'konlar
📊 Do'kon statistikasi  → Murojaatlar va reyting
📋 Murojaatlar          → Do'konga kelgan murojaatlar
⭐ Reytingim            → Xavfsizlik holati va reyting
💰 Keshbek              → Tadbirkor keshbek dasturi
```

---

## 🎛 Django Admin Panel

**URL:** `http://localhost:8000/admin/`

### Kirish:
- **Login:** `admin`
- **Parol:** `admin1234` *(o'zgartirishni unutmang!)*

### Dashboard — Bosh sahifa:

Kirganingizda premium dark theme dashboard ko'rinadi:

```
┌─────────────────────────────────────────────────────┐
│  [KPI] Foydalanuvchilar  [KPI] Murojaatlar          │
│  [KPI] Do'konlar         [KPI] Keshbek (so'm)       │
├──────────────────┬──────────────────┬───────────────┤
│  Murojaatlar     │  Do'konlar       │  So'nggi 7    │
│  holati          │  xavfsizligi     │  kun grafigi  │
│  (Donut chart)   │  (Bar chart)     │  (Line chart) │
├──────────────────┴──────────────────┴───────────────┤
│  So'nggi murojaatlar    │  So'nggi foydalanuvchilar  │
└─────────────────────────┴────────────────────────────┘
```

### Murojaatni ko'rib chiqish:

1. `Admin → Murojaatlar → Complaint` bo'limiga o'ting
2. Murojaat ID sini bosing
3. **Status** maydonini o'zgartiring (masalan: `PENDING → UNDER_REVIEW`)
4. Kerak bo'lsa **Moderator izohi** yozing
5. **Saqlash** ni bosing

> ✅ Saqlash tugmasini bosganingizda foydalanuvchiga **Telegram orqali avtomatik xabar** ketadi!

### Murojaat holatlari:

| Holat | Ma'no | Badge |
|-------|-------|-------|
| `PENDING` | Kutilmoqda (yangi kelgan) | ⬜ Grey |
| `UNDER_REVIEW` | Ko'rib chiqilmoqda | 🟡 Orange |
| `APPROVED` | Tasdiqlandi | 🔵 Blue |
| `REJECTED` | Rad etildi | 🔴 Red |
| `RESOLVED` | Hal qilindi | 🟢 Green |

---

## 💾 Ma'lumotlar bazasi modellari

### `TelegramUser` (apps/users)

```python
telegram_id    BigIntegerField   # Telegram ID (unique)
username       CharField         # @username
first_name     CharField         # Ism
last_name      CharField         # Familiya
phone_number   CharField         # Telefon raqami
role           CharField         # CONSUMER / ENTREPRENEUR / ADMIN / MODERATOR
is_active      BooleanField      # Faollik holati
created_at     DateTimeField     # Qo'shilgan vaqti
last_activity  DateTimeField     # Oxirgi faollik
```

### `Complaint` (apps/complaints)

```python
ticket_id         CharField    # SES-2026-000001 (avtomatik)
user              ForeignKey   # TelegramUser ga bog'liq
description       TextField    # Murojaat matni (max 3000)
photo_file_id     CharField    # Telegram file_id
latitude          Decimal      # GPS kenglik
longitude         Decimal      # GPS uzunlik
status            CharField    # Holat (PENDING → RESOLVED)
moderation_comment TextField   # Moderator izohi
created_at        DateTimeField
resolved_at       DateTimeField # Hal qilingan vaqti
```

### `Store` (apps/stores)

```python
name           CharField     # Do'kon nomi
address        TextField     # Manzil
latitude       Decimal       # GPS (nullable)
longitude      Decimal       # GPS (nullable)
phone          CharField     # Telefon
rating         Decimal       # 0.0 – 5.0
safety_status  CharField     # GREEN / YELLOW / RED
is_active      BooleanField
```

### `CashbackAccount` (apps/cashback)

```python
user          OneToOneField  # TelegramUser
balance       Decimal        # Joriy balans
total_earned  Decimal        # Jami olindi
total_spent   Decimal        # Jami sarflandi
```

### `CashbackTransaction` (apps/cashback)

```python
account           ForeignKey  # CashbackAccount
amount            Decimal     # Summa
transaction_type  CharField   # EARN / SPEND / ADJUSTMENT
description       TextField   # Sabab
created_at        DateTimeField
```

---

## 🔄 Bot holat mashinalari (FSM)

Murojaat yuborish jarayoni `aiogram.fsm` asosida:

```python
class ComplaintStates(StatesGroup):
    waiting_for_description = State()   # Bosqich 1: matn
    waiting_for_photo       = State()   # Bosqich 2: rasm
    waiting_for_location    = State()   # Bosqich 3: GPS
```

**Muhim:** `stores.py` dagi location handler FSM holati tekshiradi:
```python
# Agar complaint FSM da bo'lsa, location'ni complaint handler oladi
# Aks holda, store qidirish ishlaydi
if current == ComplaintStates.waiting_for_location:
    return  # complaints.py handler o'zi oladi
```

---

## 🔔 Xabardorlik tizimi

Admin paneldan murojaat holati o'zgarganda:

```
Admin saves Complaint (status changed)
    │
    ▼
admin.py → save_model() → asyncio.run(notify_complaint_status_changed())
    │
    ▼
notification_service.py → bot.send_message(telegram_id, text)
    │
    ▼
Foydalanuvchi Telegram da xabar oladi:
    "✅ Murojaatingiz tasdiqlandi.
     🎫 ID: SES-2026-000001"
```

**Xabar shablonlari:**

| Holat | Xabar |
|-------|-------|
| `UNDER_REVIEW` | 🔍 Murojaatingiz ko'rib chiqilmoqda |
| `APPROVED` | ✅ Murojaatingiz tasdiqlandi |
| `REJECTED` | ❌ Rad etildi. Sabab: {moderation_comment} |
| `RESOLVED` | ✅ Murojaatingiz bo'yicha ish yakunlandi |

---

## ⚙️ Konfiguratsiya (.env)

```env
# ── Django ───────────────────────────────────────────────
SECRET_KEY=your-very-secret-key
DEBUG=True                     # False — production da

# ── Seed ─────────────────────────────────────────────────
SEED_MODE=real                 # real yoki fake

# ── Database ─────────────────────────────────────────────
# Development uchun comment qiling (SQLite ishlatiladi)
# DATABASE_URL=postgresql://user:pass@localhost:5432/sesport

# ── Redis (FSM — Production) ─────────────────────────────
REDIS_URL=redis://localhost:6379/1
USE_REDIS=false                # true — production da

# ── Telegram Bot ──────────────────────────────────────────
BOT_TOKEN=1234567890:ABCdef...   # BotFather dan

# ── Production ───────────────────────────────────────────
ALLOWED_HOSTS=yourdomain.com
LOG_LEVEL=INFO
```

---

## 🐳 Docker deploy (Nginx Proxy Manager bilan)

> **Python 3.12+ talab qilinadi.** Kod PEP 701 f-stringlaridan foydalanadi
> (masalan `bot/routers/admin.py:171`), shu sabab Docker image `python:3.13-slim`
> asosida qurilgan. Python 3.11 da `SyntaxError` beradi.

### Arxitektura

```
Internet
   │ 80 / 443
   ▼
Nginx Proxy Manager        ← SSL termination shu yerda
   │ npm_network
   ▼
web:8000  (Django + Gunicorn + WhiteNoise)
   │ backend
   ├──► db:5432    (PostgreSQL 16)
   └──► redis:6379 (FSM storage)
             ▲
             └──── bot  (Aiogram long polling)
```

Loyiha ichida **nginx servisi yo'q** va **hech bir konteyner host'ga port
publish qilmaydi**. `db`, `redis`, `bot` faqat `backend` tarmog'ida —
NPM ularga yeta olmaydi.

### 1. NPM network nomini aniqlash

```bash
docker ps --format '{{.Names}}' | grep -i proxy
docker inspect <npm-container> \
  --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{"\n"}}{{end}}'
```

### 2. `.env` tayyorlash

```bash
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
nano .env
```

Majburiy maydonlar:

| O'zgaruvchi | Izoh |
|---|---|
| `SECRET_KEY` | Bo'sh yoki shablon bo'lsa konteyner ishga tushmaydi |
| `POSTGRES_PASSWORD` | **Xom** parol — kodlash kerak emas |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_HOST=db` | Django shulardan DB config quradi |
| `BOT_TOKEN` | BotFather'dan |
| `ALLOWED_HOSTS` | `example.com,www.example.com` — sxemasiz |
| `CSRF_TRUSTED_ORIGINS` | `https://example.com` — **sxema bilan** |
| `NPM_NETWORK` | 1-qadamda topilgan nom |

> `DATABASE_URL` ni **bo'sh qoldiring**. U ishlatilsa, parol URL ichida
> percent-encoded (`@`→`%40`), `POSTGRES_PASSWORD` da esa xom bo'lishi kerak —
> mos kelmasa `password authentication failed` beradi.

### 3. Ishga tushirish

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f web
```

Migratsiya, `collectstatic` va superuser yaratish **avtomatik** —
`docker/entrypoint.sh` ularni faqat `web` servisida bajaradi (idempotent).

### 4. Nginx Proxy Manager sozlamasi

**Proxy Hosts → Add Proxy Host → Details:**

| Maydon | Qiymat |
|---|---|
| Domain Names | `sizning-domen.uz` |
| Scheme | `http` |
| Forward Hostname / IP | `web` |
| Forward Port | `8000` |
| Cache Assets | OFF (WhiteNoise o'zi keshlaydi) |
| Block Common Exploits | ON |
| Websockets Support | ON |

**SSL tab:** sertifikat tanlang → `Force SSL` ON → `HTTP/2` ON → `HSTS` ON

**Advanced tab:**
```nginx
client_max_body_size 20m;
```

Sertifikat olingandan keyin `.env` da `ENABLE_HTTPS=true` qiling va
`docker compose up -d web` bilan qayta ishga tushiring.

> NPM **Docker'da bo'lmasa** (host'ga o'rnatilgan bo'lsa) `web` service
> nomini topa olmaydi. U holda:
> ```bash
> docker compose -f docker-compose.yml -f docker-compose.hostport.yml up -d
> ```
> va NPM'da `Forward Hostname/IP: 127.0.0.1`, `Forward Port: 2020`.

### 5. Portlar

| Port | Kim ochadi | Internetdan |
|---|---|---|
| 80, 443 | Nginx Proxy Manager | ✅ ochiq |
| 8000 | `web` (`expose`) | ❌ yopiq |
| 5432 | `db` | ❌ yopiq |
| 6379 | `redis` | ❌ yopiq |

**Firewall (UFW):**

```bash
sudo ufw default deny incoming
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
# 5432, 6379, 8000, 2020 — HECH QACHON ochilmasin
```

> ⚠️ Docker `iptables` qoidalarini UFW'dan **oldin** qo'yadi. Shu sababli
> compose'da `"2020:8000"` deb yozish UFW `deny` bo'lsa ham portni
> internetga ochib yuboradi. Loyiha shuning uchun hech qanday port
> publish qilmaydi; `hostport` overlay esa qat'iy `127.0.0.1:` bilan bog'laydi.

### 6. Backup

```bash
# Zaxira (host'ga yoziladi, konteyner ichiga emas)
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  > backup_$(date +%F).sql

# Tiklash
cat backup_2026-08-17.sql | \
  docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

### 7. Foydali buyruqlar

```bash
docker compose logs -f web
docker compose logs -f bot
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed --mode real
docker compose restart web
docker compose down          # volume'lar saqlanadi
docker compose down -v       # DIQQAT: bazani ham o'chiradi
```

---

## 📈 Loyihani kengaytirish

### Yangi router qo'shish:

1. `bot/routers/yangi_router.py` yarating
2. `bot/routers/__init__.py` ga import qo'shing
3. `bot/main.py` dagi `dp.include_router(...)` ga qo'shing

### Yangi Django app qo'shish:

```bash
python manage.py startapp myapp
mv myapp apps/myapp
```

`config/settings/base.py` ga qo'shing:
```python
INSTALLED_APPS = [
    ...
    'apps.myapp',
]
```

### Yangi bot xabardorligi:

`bot/services/notification_service.py` ga funksiya qo'shing:

```python
async def notify_my_event(telegram_id: int, data: str) -> bool:
    text = f"📢 Yangi xabar: {data}"
    return await _send(telegram_id, text)
```

### Testlarni ishga tushirish:

```bash
pytest tests/ -v

# Bitta test fayli
pytest tests/test_complaints.py -v

# Coverage bilan
pytest tests/ --cov=apps --cov-report=html
```

---

## 🔐 Xavfsizlik eslatmalari

> ⚠️ **Production'ga chiqishdan oldin:**

- [ ] `.env` da `DEBUG=False` qiling
- [ ] `SECRET_KEY` ni yangi, uzoq stringga o'zgartiring
- [ ] `ALLOWED_HOSTS` ni real domenga cheklang
- [ ] Admin paroli `admin1234` dan o'zgartiring
- [ ] `USE_REDIS=true` qiling (MemoryStorage production'da xavfsiz emas)
- [ ] HTTPS va SSL sertifikat o'rnating
- [ ] PostgreSQL ishlatish (SQLite production'da yaroqsiz)
- [ ] `BOT_TOKEN` ni hech kimga bermang

---

## 👨‍💻 Muallif

**SESPORT** loyihasi — O'zbekiston iste'molchilari uchun.

- Telegram: [@sesport_support](https://t.me/sesport_support)
- Email: support@sesport.uz

---

*Hujjat oxirgi marta yangilangan: 2026-yil avgust*
