from django.test import TestCase
from jdatetime import date as jdate
from jdatetime import datetime as jdatetime
from bookings.models import Booking
from dorms.models import Room, Dorm
from users.models import User


class BookingModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email='testuser@gmail.com',
            student_code="12345",
            national_code="987654321",
            phone_number="1234567890",
            password="password123"
        )

        # Create a test dorm and room
        self.dorm = Dorm.objects.create(name="Dorm A", location="Test Location")
        self.room = Room.objects.create(dorm=self.dorm, room_number="101", capacity=4, floor=1)

    def test_booking_jalali_dates(self):
        # Create a booking with Jalali dates
        start_date = jdate(1402, 11, 1)  # Equivalent to 2024-01-21 in Gregorian
        end_date = jdate(1402, 11, 10)   # Equivalent to 2024-01-30 in Gregorian
        booking = Booking.objects.create(
            student=self.user,
            room=self.room,
            start_date=start_date,
            end_date=end_date
        )

        # Retrieve the booking and check the dates
        self.assertEqual(booking.start_date, start_date)
        self.assertEqual(booking.end_date, end_date)

    def test_booking_created_at_jalali(self):
        # Create a booking and check the created_at field
        booking = Booking.objects.create(
            student=self.user,
            room=self.room,
            start_date=jdate(1402, 11, 1),
            end_date=jdate(1402, 11, 10)
        )
        self.assertIsNotNone(booking.created_at)
        self.assertIsInstance(booking.created_at, jdatetime)