"""
SESPORT Real Seed Data — Haqiqiy Uzbekiston ma'lumotlari.

Bu fayl real production-like ma'lumotlarni bazaga kiritadi:
- Toshkentdagi haqiqiy supermarket va do'konlar
- O'zbekiston iste'molchi huquqlari qonunchiligi
- Haqiqiy yordam kontakt ma'lumotlari
- Demo foydalanuvchilar va murojaatlar
"""
from decimal import Decimal
from django.utils import timezone


# ──────────────────────────────────────────────────────────────────────────────
# DATA
# ──────────────────────────────────────────────────────────────────────────────

REAL_STORES = [
    {
        'name': 'Korzinka Supermarket — Yunusobod',
        'address': "Toshkent sh., Yunusobod tumani, Amir Temur ko'chasi 108",
        'latitude': Decimal('41.3396'),
        'longitude': Decimal('69.2939'),
        'phone': '+998712007000',
        'rating': Decimal('4.2'),
        'safety_status': 'GREEN',
    },
    {
        'name': 'Makro — Sergeli',
        'address': "Toshkent sh., Sergeli tumani, Bunyodkor ko'chasi 12",
        'latitude': Decimal('41.2373'),
        'longitude': Decimal('69.2167'),
        'phone': '+998712007001',
        'rating': Decimal('4.0'),
        'safety_status': 'GREEN',
    },
    {
        'name': "Carrefour — Samarqand darvoza",
        'address': "Toshkent sh., Shayhontohur tumani, Shota Rustaveli ko'chasi 28",
        'latitude': Decimal('41.3003'),
        'longitude': Decimal('69.2601'),
        'phone': '+998712007002',
        'rating': Decimal('4.5'),
        'safety_status': 'GREEN',
    },
    {
        'name': 'Havas Supermarket — Mirzo Ulugbek',
        'address': "Toshkent sh., Mirzo Ulugbek tumani, Bog'ishamol ko'chasi 10",
        'latitude': Decimal('41.3270'),
        'longitude': Decimal('69.3520'),
        'phone': '+998712007003',
        'rating': Decimal('3.8'),
        'safety_status': 'YELLOW',
    },
    {
        'name': 'Smart Bozor — Olmazor',
        'address': "Toshkent sh., Olmazor tumani, Olmazor ko'chasi 55",
        'latitude': Decimal('41.3542'),
        'longitude': Decimal('69.2183'),
        'phone': '+998712007004',
        'rating': Decimal('3.5'),
        'safety_status': 'YELLOW',
    },
    {
        'name': "Globe Shopping Center — Chilonzor",
        'address': "Toshkent sh., Chilonzor tumani, Qoratosh ko'chasi 7",
        'latitude': Decimal('41.2850'),
        'longitude': Decimal('69.2040'),
        'phone': '+998712007005',
        'rating': Decimal('2.9'),
        'safety_status': 'RED',
    },
    {
        'name': 'Ramstore — Yashnobod',
        'address': "Toshkent sh., Yashnobod tumani, Farobiy ko'chasi 22",
        'latitude': Decimal('41.3050'),
        'longitude': Decimal('69.3120'),
        'phone': '+998712007006',
        'rating': Decimal('4.1'),
        'safety_status': 'GREEN',
    },
    {
        'name': "Next Market — Bektemir",
        'address': "Toshkent sh., Bektemir tumani, Sanoat ko'chasi 3",
        'latitude': Decimal('41.2700'),
        'longitude': Decimal('69.3600'),
        'phone': '+998712007007',
        'rating': Decimal('2.5'),
        'safety_status': 'RED',
    },
    {
        'name': 'Anhor Market — Uchtepa',
        'address': "Toshkent sh., Uchtepa tumani, Uchtepa ko'chasi 44",
        'latitude': Decimal('41.3120'),
        'longitude': Decimal('69.2290'),
        'phone': '+998712007008',
        'rating': Decimal('3.7'),
        'safety_status': 'YELLOW',
    },
    {
        'name': 'Supermarket "O\'zbekiston" — Zangiota',
        'address': "Toshkent viloyati, Zangiota tumani, Markaziy ko'cha 1",
        'latitude': Decimal('41.2200'),
        'longitude': Decimal('69.1800'),
        'phone': '+998712007009',
        'rating': Decimal('3.2'),
        'safety_status': 'YELLOW',
    },
]

REAL_CONSUMER_RIGHTS = [
    {
        'title': "Sifatli mahsulot olish huquqi",
        'category': "Asosiy huquqlar",
        'order': 1,
        'content': (
            "O'zbekiston Respublikasining «Iste'molchilar huquqlarini himoya qilish to'g'risida»gi Qonuniga "
            "muvofiq (16-modda), har bir iste'molchi sifatli tovar yoki xizmat olish huquqiga ega.\n\n"
            "Bu shuni anglatadiki:\n"
            "• Mahsulot e'lon qilingan xususiyatlarga mos bo'lishi kerak\n"
            "• Amal qilish muddati ko'rsatilgan bo'lishi shart\n"
            "• Muddati o'tgan mahsulot sotilishi taqiqlanadi\n"
            "• Sifatsiz mahsulot topilsa, sotuvchi uni almashtirishi yoki pul qaytarishi shart\n\n"
            "Qonuniy asos: O'zRQ 16-modda, 2019-yil 4-yanvar"
        ),
    },
    {
        'title': "To'g'ri ma'lumot olish huquqi",
        'category': "Asosiy huquqlar",
        'order': 2,
        'content': (
            "O'zbekiston Respublikasi qonunchiligiga ko'ra iste'molchi mahsulot to'g'risida "
            "to'liq va ishonchli ma'lumot olish huquqiga ega (14-modda).\n\n"
            "Sotuvchi ko'rsatishi shart:\n"
            "• Ishlab chiqaruvchi nomi va joylashuvi\n"
            "• Ishlab chiqarilgan sana va amal qilish muddati\n"
            "• Mahsulot tarkibi va xususiyatlari\n"
            "• Saqlash va foydalanish shartlari\n"
            "• Narx va o'lchov birliklari\n\n"
            "Agar ma'lumot berishdan bosh tortilsa, iste'molchi shikoyat qilish huquqiga ega."
        ),
    },
    {
        'title': "Buzilgan mahsulotni qaytarish huquqi",
        'category': "Kafolatlar",
        'order': 3,
        'content': (
            "Iste'molchi quyidagi hollarda mahsulotni qaytarishi yoki almashtirishi mumkin (21-modda):\n\n"
            "✅ Qaytarish mumkin bo'lgan holatlar:\n"
            "• Mahsulot sifatsiz chiqsa\n"
            "• Muddati o'tgan bo'lsa (xarid paytida)\n"
            "• E'lon qilingan xususiyatlardan farq qilsa\n"
            "• Kafolat muddati ichida buzilsa\n\n"
            "📋 Qaytarish muddati:\n"
            "• Oziq-ovqat mahsulotlari: 24 soat ichida\n"
            "• Sanoat tovarlari: 14 kun ichida\n"
            "• Kafolat mahsulotlari: kafolat muddati ichida\n\n"
            "Chekit yoki chek bo'lmasa ham qaytarish mumkin (guvoh kerak bo'lishi mumkin)."
        ),
    },
    {
        'title': "Zararni qoplash huquqi",
        'category': "Kompensatsiya",
        'order': 4,
        'content': (
            "Sifatsiz mahsulot yoki xizmat natijasida zarar ko'rgan iste'molchi "
            "zararni to'liq qoplash talabini qo'yishi mumkin (22-modda).\n\n"
            "Qoplash talab qilsa bo'ladi:\n"
            "• Moliyaviy zarar (kasalxona xarajatlari, yo'qotilgan daromad)\n"
            "• Moral zarar\n"
            "• Mahsulotni almashtirish narxi\n\n"
            "Murojaat qilish tartibi:\n"
            "1. Sotuvchiga yozma da'vo yuboring\n"
            "2. 10 kun ichida javob bo'lmasa — iste'molchilarni himoya qilish organiga\n"
            "3. Oxirgi instansiya — sud"
        ),
    },
    {
        'title': "Shikoyat berish huquqi va tartibi",
        'category': "Amaliy qo'llanma",
        'order': 5,
        'content': (
            "Iste'molchi quyidagi organlarga murojaat qilishi mumkin:\n\n"
            "📞 1. SESPORT bot — darhol murojaat:\n"
            "• «📝 Shikoyat qilish» tugmasini bosing\n"
            "• Rasm va joylashuvni yuboring\n"
            "• Murojaat ID olasiz\n\n"
            "📋 2. Sanitariya-epidemiologiya nazorati (SES):\n"
            "• Telefon: 1080\n"
            "• Oziq-ovqat xavfsizligi masalalarida\n\n"
            "⚖️ 3. Iste'molchilar huquqlarini himoya qilish:\n"
            "• Telefon: 1060\n"
            "• Yozma ariza bilan\n\n"
            "🏛 4. Sud:\n"
            "• Davlat boji to'lanmaydi (iste'molchi da'volari uchun)\n"
            "• Ijrochi da'vo yozib beradi"
        ),
    },
    {
        'title': "Oziq-ovqat xavfsizligi standartlari",
        'category': "Standartlar",
        'order': 6,
        'content': (
            "O'zbekistonda oziq-ovqat xavfsizligini tartibga soluvchi asosiy normalar:\n\n"
            "📌 Majburiy talablar:\n"
            "• Har bir mahsulotda UZ sifat belgisi bo'lishi kerak\n"
            "• Amal qilish muddati o'zbek va rus tilida ko'rsatilishi shart\n"
            "• Sovutilgan mahsulotlar uchun harorat rejimi saqlanishi kerak\n"
            "• Muzlatilgan mahsulotni qayta muzlatish taqiqlanadi\n\n"
            "🌡 Saqlash harorati:\n"
            "• Sut mahsulotlari: 0°C dan +6°C gacha\n"
            "• Go'sht: -18°C dan past\n"
            "• Mevalar: +2°C dan +8°C gacha\n\n"
            "Agar saqlash shartlari buzilgan bo'lsa — mahsulotni sotib olmang va murojaat yuboring."
        ),
    },
]

REAL_SUPPORT_CONFIG = {
    'phone': '+998 71 200-70-00',
    'telegram_username': 'sesport_support',
    'email': 'support@sesport.uz',
    'working_hours': "Dushanba–Juma: 09:00–18:00 (Toshkent vaqti)",
    'description': (
        "SESPORT iste'molchilarni himoya qilish platformasining rasmiy qo'llab-quvvatlash xizmati.\n\n"
        "Biz sizga quyidagi masalalar bo'yicha yordam beramiz:\n"
        "• Murojaat statusi haqida so'rovlar\n"
        "• Texnik muammolar\n"
        "• Do'konlar va reyting masalalari\n"
        "• Keshbek hisob-kitobi\n\n"
        "Ish vaqtidan tashqari murojaat qilsangiz, keyingi ish kunida javob beriladi."
    ),
}

REAL_USERS = [
    {
        'telegram_id': 100000001,
        'username': 'aziz_consumer',
        'first_name': 'Aziz',
        'last_name': 'Karimov',
        'role': 'CONSUMER',
    },
    {
        'telegram_id': 100000002,
        'username': 'malika_t',
        'first_name': 'Malika',
        'last_name': "Toshmatova",
        'role': 'CONSUMER',
    },
    {
        'telegram_id': 100000003,
        'username': 'sardor_biz',
        'first_name': 'Sardor',
        'last_name': "Xolmatov",
        'role': 'ENTREPRENEUR',
    },
]

REAL_COMPLAINTS = [
    {
        'user_telegram_id': 100000001,
        'description': (
            "Korzinka supermarketidan sotib olgan sut mahsuloti (Parmalat, 1L) ning "
            "amal qilish muddati 3 kun oldin o'tib ketgan. Dastlab muddatga e'tibor "
            "bermagandim, uyga borgach ko'rdim. Mahsulot shelfdagi boshqa mahsulotlar "
            "orasida mo'ljallangan joyda turgan edi."
        ),
        'photo_file_id': 'demo_photo_id_001',
        'latitude': Decimal('41.3396'),
        'longitude': Decimal('69.2939'),
        'status': 'PENDING',
    },
    {
        'user_telegram_id': 100000002,
        'description': (
            "Smart Bozor do'konida go'sht mahsulotlari noto'g'ri haroratda saqlanayotgani "
            "aniqlandi. Muzlatgich ishlamasdi, mahsulotlar eriy boshlagan holda sotilayotgan edi. "
            "Sotuvchiga aytdim, lekin e'tibor bermadi. Rasm tushirdim."
        ),
        'photo_file_id': 'demo_photo_id_002',
        'latitude': Decimal('41.3542'),
        'longitude': Decimal('69.2183'),
        'status': 'UNDER_REVIEW',
        'moderation_comment': None,
    },
    {
        'user_telegram_id': 100000001,
        'description': (
            "Globe Shopping Centerda muddati 2 hafta oldin o'tgan konserva mahsulotlari "
            "haligacha shelflarda turgan. Bir nechta mahsulotni tekshirdim — barchasi "
            "muddati o'tgan. Bu jiddiy xavfsizlik muammosi."
        ),
        'photo_file_id': 'demo_photo_id_003',
        'latitude': Decimal('41.2850'),
        'longitude': Decimal('69.2040'),
        'status': 'RESOLVED',
        'moderation_comment': "Tekshiruv o'tkazildi. Do'kon ogohlantirildi, mahsulotlar olib tashlandi.",
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# SEED FUNCTION
# ──────────────────────────────────────────────────────────────────────────────

def seed_real(cmd, clear: bool = False) -> None:
    """Seed with real Uzbekistan data."""
    from apps.users.models import TelegramUser
    from apps.complaints.models import Complaint
    from apps.stores.models import Store
    from apps.cashback.models import CashbackAccount, CashbackTransaction, TransactionType
    from apps.rights.models import ConsumerRight
    from apps.support.models import SupportConfiguration
    from django.db import transaction as db_tx

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

        # 1. Stores
        cmd.stdout.write("  🏪 Do'konlar kiritilmoqda...")
        store_count = 0
        for s in REAL_STORES:
            store, created = Store.objects.get_or_create(
                name=s['name'],
                defaults=s,
            )
            if created:
                store_count += 1
        cmd.stdout.write(cmd.style.SUCCESS(f"  ✓ {store_count} ta yangi do'kon kiritildi ({Store.objects.count()} jami)"))

        # 2. Consumer Rights
        cmd.stdout.write("  ⚖️  Iste'molchi huquqlari kiritilmoqda...")
        right_count = 0
        for r in REAL_CONSUMER_RIGHTS:
            right, created = ConsumerRight.objects.get_or_create(
                title=r['title'],
                defaults={**r, 'is_active': True},
            )
            if created:
                right_count += 1
        cmd.stdout.write(cmd.style.SUCCESS(f"  ✓ {right_count} ta huquq kiritildi ({ConsumerRight.objects.count()} jami)"))

        # 3. Support Config
        cmd.stdout.write("  💬 Yordam konfiguratsiyasi kiritilmoqda...")
        support, created = SupportConfiguration.objects.get_or_create(
            email=REAL_SUPPORT_CONFIG['email'],
            defaults={**REAL_SUPPORT_CONFIG, 'is_active': True},
        )
        if created:
            cmd.stdout.write(cmd.style.SUCCESS("  ✓ Yordam konfiguratsiyasi kiritildi"))
        else:
            cmd.stdout.write("  → Yordam konfiguratsiyasi allaqachon mavjud")

        # 4. Demo Users
        cmd.stdout.write("  👤 Demo foydalanuvchilar kiritilmoqda...")
        user_count = 0
        for u in REAL_USERS:
            user, created = TelegramUser.objects.get_or_create(
                telegram_id=u['telegram_id'],
                defaults=u,
            )
            if created:
                user_count += 1
                # Create cashback account for each consumer
                if u['role'] == 'CONSUMER':
                    account = CashbackAccount.objects.create(
                        user=user,
                        balance=Decimal('0.00'),
                        total_earned=Decimal('0.00'),
                        total_spent=Decimal('0.00'),
                    )
                    # Add welcome bonus
                    CashbackTransaction.objects.create(
                        account=account,
                        amount=Decimal('5000.00'),
                        transaction_type=TransactionType.EARN,
                        description='Ro\'yxatdan o\'tganlik uchun bonus',
                    )
                    account.balance = Decimal('5000.00')
                    account.total_earned = Decimal('5000.00')
                    account.save()
        cmd.stdout.write(cmd.style.SUCCESS(f"  ✓ {user_count} ta demo foydalanuvchi kiritildi"))

        # 5. Demo Complaints
        cmd.stdout.write("  📋 Demo murojaatlar kiritilmoqda...")
        complaint_count = 0
        for c in REAL_COMPLAINTS:
            user = TelegramUser.objects.filter(telegram_id=c['user_telegram_id']).first()
            if not user:
                continue
            existing = Complaint.objects.filter(
                user=user,
                description__startswith=c['description'][:50],
            ).first()
            if not existing:
                complaint = Complaint(
                    user=user,
                    description=c['description'],
                    photo_file_id=c['photo_file_id'],
                    latitude=c['latitude'],
                    longitude=c['longitude'],
                    status=c['status'],
                    moderation_comment=c.get('moderation_comment'),
                )
                if c['status'] == 'RESOLVED':
                    complaint.resolved_at = _now()
                complaint.save()
                complaint_count += 1
        cmd.stdout.write(cmd.style.SUCCESS(f"  ✓ {complaint_count} ta demo murojaat kiritildi"))

    cmd.stdout.write(cmd.style.MIGRATE_HEADING("\n📊 Real seed yakuniy statistika:"))
    cmd.stdout.write(f"  🏪 Do'konlar: {Store.objects.count()}")
    cmd.stdout.write(f"  👤 Foydalanuvchilar: {TelegramUser.objects.count()}")
    cmd.stdout.write(f"  📋 Murojaatlar: {Complaint.objects.count()}")
    cmd.stdout.write(f"  ⚖️  Huquqlar: {ConsumerRight.objects.count()}")
    cmd.stdout.write(f"  💬 Yordam: {SupportConfiguration.objects.count()}")


def _now():
    return timezone.now()
