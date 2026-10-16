from __future__ import annotations
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.users.models import TelegramUser, UserRole

class Command(BaseCommand):
    help = "Foydalanuvchini mobil ilova va Telegram bot uchun ADMIN qilish, hamda Django superuser yaratish."

    def add_arguments(self, parser):
        parser.add_argument(
            'identifier',
            type=str,
            help="Foydalanuvchi telefon raqami (+998...), Telegram username yoki Telegram ID si.",
        )
        parser.add_argument(
            '--password',
            type=str,
            default=None,
            help="Django web admin (/admin/) uchun parol (agar berilmasa, faqat mobil/bot admin qilinadi).",
        )

    def handle(self, *args, **options):
        ident = options['identifier'].strip()
        pwd = options.get('password')

        # 1. TelegramUser ni topish
        digits = ident.replace('+', '').replace(' ', '').replace('-', '')
        user = None

        if digits.isdigit() and len(digits) >= 9:
            # Phone number or Telegram ID
            user = TelegramUser.objects.filter(phone_number__icontains=digits[-9:]).first()
            if not user and len(digits) > 7:
                user = TelegramUser.objects.filter(telegram_id=int(digits)).first()
        elif ident.startswith('@'):
            user = TelegramUser.objects.filter(username__iexact=ident.lstrip('@')).first()
        else:
            user = TelegramUser.objects.filter(username__iexact=ident).first()

        if not user:
            # If user not found, list recent users to help
            recent = TelegramUser.objects.order_by('-created_at')[:5]
            recent_list = ", ".join([f"{u.full_name} ({u.phone_number or u.username})" for u in recent])
            empty_msg = "Bazada foydalanuvchilar yo'q. Avval ilovadan ro'yxatdan o'ting."
            self.stdout.write(self.style.WARNING(
                f"[!] '{ident}' bo'yicha foydalanuvchi topilmadi.\n"
                f"So'nggi foydalanuvchilar: {recent_list or empty_msg}"
            ))
            return

        # 2. Mobil/Bot rolini ADMIN ga o'zgartirish
        user.role = UserRole.ADMIN
        user.is_active = True
        user.save()

        self.stdout.write(self.style.SUCCESS(
            f"✓ Muvaffaqiyatli! {user.full_name} ({user.phone_number or user.username}) endi rasmiy ADMIN!\n"
            f"Endi mobil ilovaning 'Menyu' qismida '🛡 SESPORT Admin Paneli' ochiladi."
        ))

        # 3. Agar parol berilgan bo'lsa, Django Web Admin (/admin/) uchun ham superuser qilish
        if pwd:
            AuthUser = get_user_model()
            username = user.username or (f"admin_{user.phone_number.replace('+', '')}" if user.phone_number else f"admin_{user.id}")
            admin_user, created = AuthUser.objects.get_or_create(username=username)
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password(pwd)
            admin_user.save()

            self.stdout.write(self.style.SUCCESS(
                f"✓ Django Web Admin (/admin/) uchun ham superuser yaratildi!\n"
                f"Login: {username}\n"
                f"Parol: {pwd}"
            ))
