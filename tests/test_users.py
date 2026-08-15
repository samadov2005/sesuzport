"""
Tests for TelegramUser model and user service.
"""
import pytest
from django.test import TestCase
from apps.users.models import TelegramUser, UserRole


class TelegramUserModelTest(TestCase):
    """Test TelegramUser model."""

    def setUp(self) -> None:
        self.user_data = {
            'telegram_id': 123456789,
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
        }

    def test_create_user(self) -> None:
        """Test creating a basic user."""
        user = TelegramUser.objects.create(**self.user_data)
        self.assertIsNotNone(user.pk)
        self.assertEqual(user.telegram_id, 123456789)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, UserRole.CONSUMER)
        self.assertTrue(user.is_active)

    def test_user_unique_telegram_id(self) -> None:
        """Test that telegram_id must be unique."""
        from django.db import IntegrityError
        TelegramUser.objects.create(**self.user_data)
        with self.assertRaises(IntegrityError):
            TelegramUser.objects.create(**self.user_data)

    def test_user_full_name(self) -> None:
        """Test full_name property."""
        user = TelegramUser.objects.create(**self.user_data)
        self.assertEqual(user.full_name, 'Test User')

    def test_user_full_name_no_last_name(self) -> None:
        """Test full_name with no last name."""
        data = self.user_data.copy()
        data['last_name'] = None
        data['telegram_id'] = 999999
        user = TelegramUser.objects.create(**data)
        self.assertEqual(user.full_name, 'Test')

    def test_user_str(self) -> None:
        """Test __str__ representation."""
        user = TelegramUser.objects.create(**self.user_data)
        self.assertIn('testuser', str(user))

    def test_role_selection_consumer(self) -> None:
        """Test setting consumer role."""
        user = TelegramUser.objects.create(**self.user_data)
        user.role = UserRole.CONSUMER
        user.save()
        refreshed = TelegramUser.objects.get(pk=user.pk)
        self.assertEqual(refreshed.role, UserRole.CONSUMER)

    def test_role_selection_entrepreneur(self) -> None:
        """Test setting entrepreneur role."""
        user = TelegramUser.objects.create(**self.user_data)
        user.role = UserRole.ENTREPRENEUR
        user.save()
        refreshed = TelegramUser.objects.get(pk=user.pk)
        self.assertEqual(refreshed.role, UserRole.ENTREPRENEUR)

    def test_user_get_or_create(self) -> None:
        """Test get_or_create pattern."""
        user1, created1 = TelegramUser.objects.get_or_create(
            telegram_id=self.user_data['telegram_id'],
            defaults=self.user_data,
        )
        self.assertTrue(created1)

        user2, created2 = TelegramUser.objects.get_or_create(
            telegram_id=self.user_data['telegram_id'],
            defaults=self.user_data,
        )
        self.assertFalse(created2)
        self.assertEqual(user1.pk, user2.pk)

    def test_user_is_active_default(self) -> None:
        """Test that users are active by default."""
        user = TelegramUser.objects.create(**self.user_data)
        self.assertTrue(user.is_active)

    def test_user_without_username(self) -> None:
        """Test creating user without username."""
        data = self.user_data.copy()
        data['username'] = None
        data['telegram_id'] = 777777
        user = TelegramUser.objects.create(**data)
        self.assertIsNone(user.username)

    def test_user_queryset_ordering(self) -> None:
        """Test that users are ordered by created_at descending."""
        TelegramUser.objects.create(telegram_id=111, first_name='First')
        TelegramUser.objects.create(telegram_id=222, first_name='Second')
        users = TelegramUser.objects.all()
        # Second user should come first (newer)
        self.assertEqual(users[0].first_name, 'Second')
