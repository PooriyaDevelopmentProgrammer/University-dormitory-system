from django.test import TestCase
from django.contrib.auth import get_user_model
from dorms.models import Room, Dorm
from bookings.models import Booking
from datetime import date

User = get_user_model()


class BookingModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            student_code="12345",
            national_code="987654321",
            phone_number="1234567890",
            password="password123"
        )
        self.dorm = Dorm.objects.create(name='dorm A', location='this is just test', gender_restriction='male')
        self.room = Room.objects.create(room_number="201", dorm=self.dorm, capacity=2, floor=2)

    def test_create_booking(self):
        # Create a booking
        booking = Booking.objects.create(
            student=self.user,
            room=self.room,
            status=Booking.BookingStatus.PENDING,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 10)
        )
        self.assertEqual(str(booking), f"Booking by {self.user.student_code} (pending)")
        self.assertEqual(booking.status, Booking.BookingStatus.PENDING)

    def test_booking_status_update(self):
        # Create a booking
        booking = Booking.objects.create(
            student=self.user,
            room=self.room,
            status=Booking.BookingStatus.PENDING,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 10)
        )
        # Update the status
        booking.status = Booking.BookingStatus.APPROVED
        booking.save()
        self.assertEqual(booking.status, Booking.BookingStatus.APPROVED)

"""
class BookingHistoryModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            student_code="12345",
            national_code="987654321",
            phone_number="1234567890",
            password="password123"
        )
        self.dorm = Dorm.objects.create(name='dorm A', location='this is just test', gender_restriction='male')
        self.room = Room.objects.create(room_number="201", dorm=self.dorm, capacity=2, floor=2)

        # Create a booking
        self.booking = Booking.objects.create(
            student=self.user,
            room=self.room,
            status=Booking.BookingStatus.PENDING,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 10)
        )

    def test_create_booking_history(self):
        # Create a booking history record
        history = BookingHistory.objects.create(
            booking=self.booking,
            status=Booking.BookingStatus.APPROVED,
            changed_by=self.user
        )
        self.assertEqual(str(history), f"{self.booking} changed to approved")
        self.assertEqual(history.status, Booking.BookingStatus.APPROVED)
        self.assertEqual(history.changed_by, self.user)
"""