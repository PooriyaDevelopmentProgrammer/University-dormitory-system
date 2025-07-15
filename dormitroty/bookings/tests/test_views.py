from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from dorms.models import Dorm, Room
from bookings.models import Booking

User = get_user_model()

class BookingListCreateAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            student_code="12345",
            national_code="987654321",
            phone_number="1234567890",
            password="password123"
        )
        self.admin_user = User.objects.create_superuser(
            email="testadminuser@example.com",
            student_code="12346",
            national_code="987654322",
            phone_number="1234567891",
            password="password124"
        )
        self.client.force_authenticate(user=self.user)
        self.client.force_authenticate(user=self.admin_user)


        # Create a test dorm and room
        self.dorm = Dorm.objects.create(name="Dorm A")
        self.room = Room.objects.create(dorm=self.dorm, full=False, floor=2,capacity=4)

        # Create a test booking
        self.booking = Booking.objects.create(
            student=self.user,
            bed=None,
            status=Booking.BookingStatus.PENDING,
            start_date="2023-01-01",
            end_date="2023-01-10"
        )

    def test_get_bookings(self):

        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], Booking.BookingStatus.PENDING)

    def test_create_booking_success(self):
        data = {
            "dorm_id": self.dorm.id,
            "room_id": self.room.id,
            "start_date": "2023-02-01",
            "end_date": "2023-02-10"
        }
        response = self.client.post('/api/bookings/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], Booking.BookingStatus.PENDING)

    def test_create_booking_invalid_room(self):
        data = {
            "dorm_id": self.dorm.id,
            "room_id": 999,
            "start_date": "2023-02-01",
            "end_date": "2023-02-10"
        }
        response = self.client.post('/api/bookings/', data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("اتاق انتخاب‌شده در این خوابگاه وجود ندارد.", str(response.data['non_field_errors'][0]))

    def test_create_booking_room_full(self):
        self.room.full = True
        self.room.save()
        data = {
            "dorm_id": self.dorm.id,
            "room_id": self.room.id,
            "start_date": "2023-02-01",
            "end_date": "2023-02-10"
        }
        response = self.client.post('/api/bookings/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ظرفیت این اتاق تکمیل شده است.", str(response.data))