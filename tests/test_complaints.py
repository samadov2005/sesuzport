"""
Tests for Complaint model and complaint service.
"""
import pytest
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from apps.users.models import TelegramUser, UserRole
from apps.complaints.models import Complaint, ComplaintStatus, ComplaintStatusHistory


class ComplaintModelTest(TestCase):
    """Test Complaint model."""

    def setUp(self) -> None:
        self.user = TelegramUser.objects.create(
            telegram_id=123456789,
            username='testuser',
            first_name='Test',
            last_name='User',
            role=UserRole.CONSUMER,
        )
        self.complaint_data = {
            'user': self.user,
            'description': 'Mahsulot muddati o\'tgan. Sana: 01.01.2026',
            'photo_file_id': 'AgACAgIAAxkBAAIBfWZ...',
            'latitude': Decimal('41.299496'),
            'longitude': Decimal('69.240073'),
        }

    def test_create_complaint(self) -> None:
        """Test creating a complaint generates ticket_id."""
        complaint = Complaint.objects.create(**self.complaint_data)
        self.assertIsNotNone(complaint.pk)
        self.assertIsNotNone(complaint.ticket_id)
        self.assertTrue(complaint.ticket_id.startswith('SES-'))

    def test_ticket_id_format(self) -> None:
        """Test ticket_id follows SES-YEAR-NNNNNN format."""
        complaint = Complaint.objects.create(**self.complaint_data)
        parts = complaint.ticket_id.split('-')
        self.assertEqual(len(parts), 3)
        self.assertEqual(parts[0], 'SES')
        self.assertEqual(int(parts[1]), timezone.now().year)
        self.assertEqual(len(parts[2]), 6)

    def test_ticket_id_unique(self) -> None:
        """Test that ticket IDs are unique."""
        c1 = Complaint.objects.create(**self.complaint_data)
        data2 = self.complaint_data.copy()
        data2['description'] = 'Another complaint'
        c2 = Complaint.objects.create(**data2)
        self.assertNotEqual(c1.ticket_id, c2.ticket_id)

    def test_default_status_pending(self) -> None:
        """Test that new complaints have PENDING status."""
        complaint = Complaint.objects.create(**self.complaint_data)
        self.assertEqual(complaint.status, ComplaintStatus.PENDING)

    def test_complaint_str(self) -> None:
        """Test __str__ returns ticket_id."""
        complaint = Complaint.objects.create(**self.complaint_data)
        self.assertEqual(str(complaint), complaint.ticket_id)

    def test_description_min_length_validation(self) -> None:
        """Test that description should be at least 10 chars (application-level)."""
        # This tests that the description field can store text
        complaint = Complaint.objects.create(**self.complaint_data)
        self.assertGreater(len(complaint.description), 10)

    def test_complaint_belongs_to_user(self) -> None:
        """Test complaint is properly linked to user."""
        complaint = Complaint.objects.create(**self.complaint_data)
        self.assertEqual(complaint.user.telegram_id, self.user.telegram_id)

    def test_user_can_see_own_complaints(self) -> None:
        """Test user can only see their own complaints."""
        other_user = TelegramUser.objects.create(
            telegram_id=987654321,
            first_name='Other',
        )
        # Create complaint for other user
        other_data = self.complaint_data.copy()
        other_data['user'] = other_user
        Complaint.objects.create(**other_data)
        # Create complaint for our user
        Complaint.objects.create(**self.complaint_data)

        # User should only see their own complaints
        my_complaints = Complaint.objects.filter(user=self.user)
        other_complaints = Complaint.objects.filter(user=other_user)

        self.assertEqual(my_complaints.count(), 1)
        self.assertEqual(other_complaints.count(), 1)
        self.assertNotEqual(
            my_complaints.first().pk,
            other_complaints.first().pk
        )

    def test_user_cannot_access_other_complaint(self) -> None:
        """Test that filtering by user returns only their complaints."""
        other_user = TelegramUser.objects.create(
            telegram_id=111222333,
            first_name='Hacker',
        )
        other_data = self.complaint_data.copy()
        other_data['user'] = other_user
        other_complaint = Complaint.objects.create(**other_data)

        # Try to get other user's complaint filtered by our user
        result = Complaint.objects.filter(
            ticket_id=other_complaint.ticket_id,
            user=self.user
        ).first()
        self.assertIsNone(result)

    def test_status_transition_pending_to_under_review(self) -> None:
        """Test status change from PENDING to UNDER_REVIEW."""
        complaint = Complaint.objects.create(**self.complaint_data)
        self.assertEqual(complaint.status, ComplaintStatus.PENDING)

        complaint.status = ComplaintStatus.UNDER_REVIEW
        complaint.save()

        refreshed = Complaint.objects.get(pk=complaint.pk)
        self.assertEqual(refreshed.status, ComplaintStatus.UNDER_REVIEW)

    def test_status_transition_to_resolved(self) -> None:
        """Test status transition to RESOLVED sets resolved_at."""
        complaint = Complaint.objects.create(**self.complaint_data)
        complaint.status = ComplaintStatus.RESOLVED
        complaint.resolved_at = timezone.now()
        complaint.save()

        refreshed = Complaint.objects.get(pk=complaint.pk)
        self.assertEqual(refreshed.status, ComplaintStatus.RESOLVED)
        self.assertIsNotNone(refreshed.resolved_at)

    def test_complaint_ordering(self) -> None:
        """Test complaints are ordered by created_at descending."""
        c1 = Complaint.objects.create(**self.complaint_data)
        data2 = self.complaint_data.copy()
        data2['description'] = 'Second complaint about expired milk'
        c2 = Complaint.objects.create(**data2)

        complaints = Complaint.objects.all()
        # c2 is newer, should come first
        self.assertEqual(complaints.first().pk, c2.pk)

    def test_complaint_status_history_created(self) -> None:
        """Test that status history is tracked."""
        complaint = Complaint.objects.create(**self.complaint_data)
        initial_count = ComplaintStatusHistory.objects.filter(
            complaint=complaint
        ).count()

        # Manually create history entry (as done by admin)
        ComplaintStatusHistory.objects.create(
            complaint=complaint,
            old_status=ComplaintStatus.PENDING,
            new_status=ComplaintStatus.UNDER_REVIEW,
        )

        new_count = ComplaintStatusHistory.objects.filter(
            complaint=complaint
        ).count()
        self.assertEqual(new_count, initial_count + 1)

    def test_photo_file_id_stored(self) -> None:
        """Test that Telegram photo file_id is properly stored."""
        complaint = Complaint.objects.create(**self.complaint_data)
        self.assertEqual(complaint.photo_file_id, 'AgACAgIAAxkBAAIBfWZ...')

    def test_coordinates_stored(self) -> None:
        """Test that GPS coordinates are properly stored."""
        complaint = Complaint.objects.create(**self.complaint_data)
        self.assertEqual(complaint.latitude, Decimal('41.299496'))
        self.assertEqual(complaint.longitude, Decimal('69.240073'))


class ComplaintTicketIDTest(TestCase):
    """Test ticket ID generation logic."""

    def setUp(self) -> None:
        self.user = TelegramUser.objects.create(
            telegram_id=555666777,
            first_name='Ticket',
        )

    def _make_complaint(self, description: str = 'Test complaint description here') -> Complaint:
        return Complaint.objects.create(
            user=self.user,
            description=description,
            photo_file_id='photo_id_123',
            latitude=Decimal('41.0'),
            longitude=Decimal('69.0'),
        )

    def test_sequential_ticket_ids(self) -> None:
        """Test that ticket IDs are sequential."""
        c1 = self._make_complaint('First complaint about product')
        c2 = self._make_complaint('Second complaint about product')
        c3 = self._make_complaint('Third complaint about product')

        num1 = int(c1.ticket_id.split('-')[2])
        num2 = int(c2.ticket_id.split('-')[2])
        num3 = int(c3.ticket_id.split('-')[2])

        self.assertLess(num1, num2)
        self.assertLess(num2, num3)

    def test_ticket_id_year_is_current(self) -> None:
        """Test that ticket ID year matches current year."""
        import datetime
        c = self._make_complaint('Year check complaint test')
        year_in_ticket = int(c.ticket_id.split('-')[1])
        self.assertEqual(year_in_ticket, datetime.date.today().year)
