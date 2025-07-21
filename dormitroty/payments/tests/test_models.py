from django.test import TestCase
from django.contrib.auth import get_user_model
from dorms.models import Dorm, Room
from bookings.models import Booking
from payments.models import Transaction
from datetime import date

User = get_user_model()


class TransactionModelTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="testuser@gmail.com",
            national_code='1234567890',
            phone_number='09123456789',
            student_code='1234',
            password='pass'
        )
        self.dorm = Dorm.objects.create(name="خوابگاه یک", location="تهران")
        self.room = Room.objects.create(
            dorm=self.dorm,
            room_number='101',
            capacity=2,
            floor=1,
            price=300000  # 300 هزار تومان
        )
        self.booking = Booking.objects.create(
            student=self.student,
            room=self.room,
            start_date=date(2025, 7, 1),
            end_date=date(2025, 9, 1),
        )
        self.transaction = Transaction.objects.create(
            student=self.student,
            booking=self.booking,
            amount=self.room.price,
            status='pending'
        )

    def test_transaction_created_correctly(self):
        self.assertEqual(self.transaction.student, self.student)
        self.assertEqual(self.transaction.booking, self.booking)
        self.assertEqual(self.transaction.amount, 300000)
        self.assertEqual(self.transaction.status, 'pending')

    def test_str_representation(self):
        expected = f"{self.student.student_code} - {self.transaction.amount} تومان - pending"
        self.assertEqual(str(self.transaction), expected)

    def test_mark_as_paid(self):
        self.transaction.mark_as_paid(ref_id='XYZ123456')
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.status, 'paid')
        self.assertEqual(self.transaction.ref_id, 'XYZ123456')
        self.booking.refresh_from_db()
