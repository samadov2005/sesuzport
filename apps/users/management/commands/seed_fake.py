"""
SESPORT Fake Seed Data — Faker bilan generatsiya qilingan test ma'lumotlari.

UI/funksiya testlari uchun ko'p miqdorda ma'lumot kiritadi:
- 50 ta random foydalanuvchi
- 30 ta random do'kon (Toshkent koordinatalarida)
- 100 ta random murojaat
- Keshbek tranzaksiyalar
- Consumer rights (Uzbek tilida)
- Support config
"""
import random
from decimal import Decimal

from django.utils import timezone


# ─── Uzbek fake data pools ─────────────────────────────────────────────────

UZBEK_FIRST_NAMES_M = [
    'Jasur', 'Sardor', 'Bobur', 'Nodir', 'Ulugbek', 'Sherzod', 'Firdavs',
    'Doniyor', 'Mirzo', 'Akbar', 'Sanjar', 'Zafar', 'Orif', 'Kamol', 'Lochinbek',
]
UZBEK_FIRST_NAMES_F = [
    'Malika', 'Feruza', 'Ozoda', 'Dilorom', 'Mohira', 'Nilufar', 'Sabina',
    'Zulfiya', 'Barno', 'Gulnora', 'Madina', 'Nargiza', 'Hilola', 'Saodat', 'Lobar',
]
UZBEK_LAST_NAMES = [
    'Karimov', 'Rahimov', 'Toshmatov', 'Xolmatov', 'Mirzayev', 'Hasanov',
    'Usmonov', 'Qodirov', 'Aliyev', 'Ergashev', 'Nazarov', 'Yunusov',
    'Abdullayev', 'Razzaqov', 'Sultonov', 'Ismoilov', 'Mamatov', 'Yusupov',
]
TASHKENT_DISTRICTS = [
    ("Yunusobod", Decimal('41.3396'), Decimal('69.2939')),
    ("Chilonzor", Decimal('41.2850'), Decimal('69.2040')),
    ("Mirzo Ulugbek", Decimal('41.3270'), Decimal('69.3520')),
    ("Sergeli", Decimal('41.2373'), Decimal('69.2167')),
    ("Olmazor", Decimal('41.3542'), Decimal('69.2183')),
    ("Shayhontohur", Decimal('41.3003'), Decimal('69.2601')),
    ("Yashnobod", Decimal('41.3050'), Decimal('69.3120')),
    ("Uchtepa", Decimal('41.3120'), Decimal('69.2290')),
    ("Bektemir", Decimal('41.2700'), Decimal('69.3600')),
    ("Shayxantahur", Decimal('41.2990'), Decimal('69.2710')),
]
STORE_NAMES_PREFIXES = [
    'Smart', 'Mega', 'Super', 'Golden', 'Star', 'Royal', 'Premium', 'City',
    'Family', 'Fresh', 'Vita', 'Green', 'Blue', 'Express',
]
STORE_NAMES_SUFFIXES = [
    'Market', 'Supermarket', 'Bozor', 'Do\'kon', 'Shop', 'Store', 'Magazin',
    'Center', 'Outlet',
]
PRODUCT_ISSUES = [
    "Muddati o'tgan sut mahsuloti (yogurt, {brand}) — shelfdagi muddatdan {days} kun oshgan.",
    "Go'sht mahsuloti noto'g'ri haroratda saqlangan, muzlatgich ishlamayotgan edi.",
    "Non mahsulotida mog'or topildi, ammo mahsulot sotilayotgan edi.",
    "Baliq konservasi — muddati {days} kun oldin o'tgan, lekin shelfdagi edi.",
    "Bolalar ovqati ({brand}) muddati o'tgan, narx belgisi ham noto'g'ri.",
    "Import mahsulot (gazak) da o'zbek tilida ma'lumot yo'q — qonun buzilishi.",
    "Qandolat mahsulotlari shisha idishda ham muhrlangan emas, tarkibi ko'rsatilmagan.",
    "Sabzavotlar chirib ketgan, lekin shelfdagi narxlar bilan sotilmoqda.",
    "Ichimlik (sut, 0.5L) muddati bugun tugaydi, lekin doimiy texnik xizmat ko'rsatilmasdi.",
    "Sovuq stende harorat +12°C (norma +4°C) — barcha sut mahsulotlari xavfli.",
]
BRANDS = ['Parmalat', 'Lactel', 'Zrazy', 'Goya', 'Nestle', 'Danone', 'Kraft']
MODERATOR_COMMENTS = [
    "Tekshiruv o'tkazildi. Muammo tasdiqlandi, sotuvchi ogohlantirildi.",
    "Do'konga sanitariya nazorati yuborildi.",
    "Muammo allaqachon hal qilingan — mahsulotlar olib tashlangan.",
    "Aloqa o'rnatildi, 3 kun ichida qayta tekshiriladi.",
    "Rad etildi: taqdim etilgan ma'lumot yetarli emas. Qayta murojaat qiling.",
]
COMPLAINT_STATUSES = ['PENDING', 'UNDER_REVIEW', 'APPROVED', 'REJECTED', 'RESOLVED']
COMPLAINT_STATUS_WEIGHTS = [40, 25, 15, 10, 10]


def _rand_coord_near(base: Decimal, max_delta: float = 0.05) -> Decimal:
    delta = Decimal(str(round(random.uniform(-max_delta, max_delta), 6)))
    return base + delta


def _rand_name() -> tuple[str, str]:
    gender = random.choice(['M', 'F'])
    fn = random.choice(UZBEK_FIRST_NAMES_M if gender == 'M' else UZBEK_FIRST_NAMES_F)
    ln = random.choice(UZBEK_LAST_NAMES)
    return fn, ln


def seed_fake(cmd, clear: bool = False) -> None:
    """Seed with fake generated data."""
    from apps.users.models import TelegramUser
    from apps.complaints.models import Complaint
    from apps.stores.models import Store
    from apps.cashback.models import CashbackAccount, CashbackTransaction, TransactionType
    from apps.rights.models import ConsumerRight
    from apps.support.models import SupportConfiguration
    from django.db import transaction as db_tx

    random.seed(42)  # reproducible fake data

    with db_tx.atomic():
        if clear:
            cmd.stdout.write("  🗑  Ma'lumotlar tozalanmoqda...")
            CashbackTransaction.objects.all().delete()
            CashbackAccount.objects.all().delete()
            Complaint.objects.all().delete()
            Store.objects.all().delete()
            ConsumerRight.objects.all().delete()
            SupportConfiguration.objects.all().delete()
            TelegramUser.objects.all().delete()
            cmd.stdout.write(cmd.style.WARNING("  ✓ Barcha ma'lumotlar tozalandi"))

        # 1. Fake Stores (30 ta)
        cmd.stdout.write("  🏪 30 ta fake do'kon yaratilmoqda...")
        store_count = 0
        for i in range(30):
            district, base_lat, base_lon = random.choice(TASHKENT_DISTRICTS)
            name = f"{random.choice(STORE_NAMES_PREFIXES)} {random.choice(STORE_NAMES_SUFFIXES)} — {district}"
            safety = random.choices(
                ['GREEN', 'YELLOW', 'RED'], weights=[60, 30, 10]
            )[0]
            rating = Decimal(str(round(random.uniform(2.0, 5.0), 1)))
            store, created = Store.objects.get_or_create(
                name=name,
                defaults={
                    'address': f"Toshkent sh., {district} tumani, Ko'cha {i+1}",
                    'latitude': _rand_coord_near(base_lat, 0.03),
                    'longitude': _rand_coord_near(base_lon, 0.03),
                    'phone': f"+99871200{7000 + i:04d}",
                    'rating': rating,
                    'safety_status': safety,
                    'is_active': True,
                },
            )
            if created:
                store_count += 1
        cmd.stdout.write(cmd.style.SUCCESS(f"  ✓ {store_count} ta fake do'kon yaratildi"))

        # 2. Consumer Rights (fake placeholder)
        cmd.stdout.write("  ⚖️  Fake huquqlar kiritilmoqda...")
        fake_rights = [
            ("Test: Sifatli mahsulot", "Asosiy", 1, "Bu test ma'lumot — sifatli mahsulot haqida."),
            ("Test: Muddatlar", "Standartlar", 2, "Bu test ma'lumot — muddatlar haqida."),
            ("Test: Qaytarish", "Kafolatlar", 3, "Bu test ma'lumot — qaytarish haqida."),
        ]
        right_count = 0
        for title, cat, order, content in fake_rights:
            r, created = ConsumerRight.objects.get_or_create(
                title=title,
                defaults={'category': cat, 'order': order, 'content': content, 'is_active': True},
            )
            if created:
                right_count += 1
        cmd.stdout.write(cmd.style.SUCCESS(f"  ✓ {right_count} ta fake huquq yaratildi"))

        # 3. Support (fake)
        support, created = SupportConfiguration.objects.get_or_create(
            email='fake-support@test.sesport.uz',
            defaults={
                'phone': '+998 71 000-00-00',
                'telegram_username': 'sesport_test',
                'working_hours': '24/7 (fake)',
                'description': 'Bu FAKE test qo\'llab-quvvatlash konfiguratsiyasi.',
                'is_active': True,
            },
        )

        # 4. Fake Users (50 ta)
        cmd.stdout.write("  👤 50 ta fake foydalanuvchi yaratilmoqda...")
        created_users = []
        user_count = 0
        base_id = 200000000
        for i in range(50):
            fn, ln = _rand_name()
            role = random.choices(['CONSUMER', 'ENTREPRENEUR'], weights=[85, 15])[0]
            tg_id = base_id + i
            user, created = TelegramUser.objects.get_or_create(
                telegram_id=tg_id,
                defaults={
                    'username': f"fake_user_{i:03d}",
                    'first_name': fn,
                    'last_name': ln,
                    'role': role,
                    'is_active': True,
                },
            )
            if created:
                user_count += 1
                created_users.append(user)
                # Cashback for consumers
                if role == 'CONSUMER':
                    balance = Decimal(str(random.randint(0, 50000)))
                    earned = balance + Decimal(str(random.randint(0, 20000)))
                    spent = earned - balance
                    account = CashbackAccount.objects.create(
                        user=user,
                        balance=balance,
                        total_earned=earned,
                        total_spent=max(Decimal('0'), spent),
                    )
                    # 1-5 ta tranzaksiya
                    for j in range(random.randint(1, 5)):
                        tx_type = random.choices(
                            [TransactionType.EARN, TransactionType.SPEND],
                            weights=[70, 30]
                        )[0]
                        amount = Decimal(str(random.randint(1000, 15000)))
                        CashbackTransaction.objects.create(
                            account=account,
                            amount=amount,
                            transaction_type=tx_type,
                            description=random.choice([
                                'Murojaat uchun bonus',
                                'Sovg\'a karta',
                                "Do'kon xaridi",
                                'Haftalik bonus',
                                'Referal bonus',
                            ]),
                        )
        cmd.stdout.write(cmd.style.SUCCESS(f"  ✓ {user_count} ta fake foydalanuvchi yaratildi"))

        # 5. Fake Complaints (100 ta)
        cmd.stdout.write("  📋 100 ta fake murojaat yaratilmoqda...")
        all_consumer_users = list(TelegramUser.objects.filter(role='CONSUMER'))
        all_stores = list(Store.objects.all())
        complaint_count = 0

        if all_consumer_users and all_stores:
            for i in range(100):
                user = random.choice(all_consumer_users)
                store = random.choice(all_stores)
                status = random.choices(COMPLAINT_STATUSES, weights=COMPLAINT_STATUS_WEIGHTS)[0]
                issue_template = random.choice(PRODUCT_ISSUES)
                description = issue_template.format(
                    brand=random.choice(BRANDS),
                    days=random.randint(1, 15),
                )
                complaint = Complaint(
                    user=user,
                    description=description,
                    photo_file_id=f'fake_photo_{i:04d}',
                    latitude=store.latitude or Decimal('41.3000'),
                    longitude=store.longitude or Decimal('69.2500'),
                    status=status,
                )
                if status in ('REJECTED',):
                    complaint.moderation_comment = random.choice(MODERATOR_COMMENTS)
                elif status == 'RESOLVED':
                    complaint.moderation_comment = random.choice(MODERATOR_COMMENTS[:3])
                    complaint.resolved_at = timezone.now()
                complaint.save()
                complaint_count += 1
        cmd.stdout.write(cmd.style.SUCCESS(f"  ✓ {complaint_count} ta fake murojaat yaratildi"))

    cmd.stdout.write(cmd.style.MIGRATE_HEADING("\n📊 Fake seed yakuniy statistika:"))
    cmd.stdout.write(f"  🏪 Do'konlar: {Store.objects.count()}")
    cmd.stdout.write(f"  👤 Foydalanuvchilar: {TelegramUser.objects.count()}")
    cmd.stdout.write(f"  📋 Murojaatlar: {Complaint.objects.count()}")
    cmd.stdout.write(f"  ⚖️  Huquqlar: {ConsumerRight.objects.count()}")
    cmd.stdout.write(f"  💳 Cashback akkauntlar: {CashbackAccount.objects.count()}")
    cmd.stdout.write(f"  🔄 Tranzaksiyalar: {CashbackTransaction.objects.count()}")
