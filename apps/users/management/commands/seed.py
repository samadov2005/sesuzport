"""
SESPORT Seed Data Management Command.

Usage:
    python manage.py seed                    # Uses SEED_MODE from .env
    python manage.py seed --mode real        # Real Uzbekistan data
    python manage.py seed --mode fake        # Faker-generated test data
    python manage.py seed --mode real --clear  # Clear all data first
    python manage.py seed --mode fake --clear

Control via .env:
    SEED_MODE=real   → Real data (production-like Uzbekistan stores, rights, etc.)
    SEED_MODE=fake   → Faker random data (for testing UI/features)
"""
import os
import logging
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Seed the database with either REAL (production-like) or FAKE (test) data.\n"
        "Set SEED_MODE=real or SEED_MODE=fake in .env to control default mode.\n"
        "Use --clear to wipe existing seed data before seeding."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            choices=['real', 'fake'],
            default=None,
            help='Seed mode: "real" (Uzbekistan data) or "fake" (generated). '
                 'Defaults to SEED_MODE env var.',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding.',
        )

    def handle(self, *args, **options):
        mode = options['mode'] or os.environ.get('SEED_MODE', 'real').lower()
        clear = options['clear']

        if mode not in ('real', 'fake'):
            raise CommandError(
                f"Invalid SEED_MODE='{mode}'. Must be 'real' or 'fake'."
            )

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n[SESPORT] Seed mode: {mode.upper()}"
            + (" (with --clear)" if clear else "")
        ))

        if mode == 'real':
            from .seed_real import seed_real
            seed_real(self, clear=clear)
        else:
            from .seed_fake import seed_fake
            seed_fake(self, clear=clear)

        self.stdout.write(self.style.SUCCESS(
            f"\n[OK] Seed ({mode}) muvaffaqiyatli yakunlandi!\n"
            f"Admin: http://localhost:8000/admin/\n"
            f"Login: admin / admin1234"
        ))
