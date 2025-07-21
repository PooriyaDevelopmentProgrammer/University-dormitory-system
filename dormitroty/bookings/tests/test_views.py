from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from bookings.pagination import StandardResultsSetPagination
from dorms.models import Dorm, Room, Bed
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
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]['status'], Booking.BookingStatus.PENDING)

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

class BookingListAccessLevelTest(APITestCase):
    def setUp(self):
        # Create a normal user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            student_code="12345",
            national_code="987654321",
            phone_number="1234567890",
            password="password123"
        )

        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            email="testadmin@example.com",
            student_code="54321",
            national_code="123456789",
            phone_number="0987654321",
            password="adminpassword"
        )

        # Create a test dorm and room
        self.dorm = Dorm.objects.create(name="Dorm A")
        self.room = Room.objects.create(dorm=self.dorm, full=False, floor=2, capacity=4)

        # Create bookings for the normal user
        self.booking1 = Booking.objects.create(
            student=self.user,
            bed=None,
            status=Booking.BookingStatus.PENDING,
            start_date="2023-01-01",
            end_date="2023-01-10"
        )

        # Create bookings for another user
        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            student_code="67890",
            national_code="987654322",
            phone_number="1234567899",
            password="password456"
        )
        self.booking2 = Booking.objects.create(
            student=self.other_user,
            bed=None,
            status=Booking.BookingStatus.PENDING,
            start_date="2023-02-01",
            end_date="2023-02-10"
        )

    def test_get_bookings_with_pagination_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']),
                         min(len(Booking.objects.all()), StandardResultsSetPagination.page_size))

    def test_get_bookings_with_pagination_as_normal_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), min(len(Booking.objects.filter(student=self.user)),
                                                            StandardResultsSetPagination.page_size))
class BookingDetailAPITest(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            student_code="12345",
            national_code="987654321",
            phone_number="1234567890",
            password="password123"
        )
        self.client.force_authenticate(user=self.user)

        # Create a test dorm and room
        self.dorm = Dorm.objects.create(name="Dorm A")
        self.room = Room.objects.create(dorm=self.dorm, full=False, floor=2, capacity=4)
        self.bed = Bed.objects.create(room=self.room, is_occupied=False)
        self.room.resequence_beds_for_room()
        # Create a test booking
        self.booking = Booking.objects.create(
            student=self.user,
            room=self.room,
            status=Booking.BookingStatus.PENDING,
            start_date="2023-01-01",
            end_date="2023-01-10"
        )

    def test_get_booking_details(self):
        response = self.client.get(f'/api/bookings/details/{self.booking.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.booking.id)

    def test_update_booking(self):
        updated_data = {
            "status": Booking.BookingStatus.APPROVED,
            "bed": self.bed.id,
            "start_date": "2023-01-05",
            "end_date": "2023-01-15"
        }
        response = self.client.put(f'/api/bookings/details/{self.booking.id}/', data=updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bed.objects.first().is_occupied, True)
        self.assertEqual(response.data['status'], Booking.BookingStatus.APPROVED)
        self.assertEqual(response.data['start_date'], "2023-01-05")
        self.assertEqual(response.data['end_date'], "2023-01-15")

    def test_delete_booking_with_bed(self):
        # Assign a bed to the booking
        self.booking.bed = self.bed
        self.booking.save()
        self.bed.is_occupied = True
        self.bed.save()

        # Ensure the bed is occupied before deletion
        self.assertTrue(self.bed.is_occupied)

        # Perform the delete request
        response = self.client.delete(f'/api/bookings/details/{self.booking.id}/')

        # Assert the response status
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Assert the booking is deleted
        self.assertFalse(Booking.objects.filter(id=self.booking.id).exists())

        # Assert the bed is no longer occupied
        self.bed.refresh_from_db()
        self.assertFalse(self.bed.is_occupied)


class BookingGenderRestrictionTest(APITestCase):
    def setUp(self):
        self.male_user = User.objects.create_user(
            student_code='1001', national_code='1234567890',
            phone_number='09120000000', gender='male'
        )
        self.female_user = User.objects.create_user(
            student_code='1002', national_code='1234567891',
            phone_number='09120000001', gender='female'
        )

        self.male_dorm = Dorm.objects.create(name="Alborz", location="North", gender_restriction="male")
        self.room = Room.objects.create(dorm=self.male_dorm, room_number='101', capacity=1, floor=1)
        self.bed = Bed.objects.create(room=self.room, bed_number='1', is_occupied=False)

    def test_female_cannot_book_male_dorm(self):
        self.client.force_authenticate(user=self.female_user)
        url = reverse('booking-list-create')
        data = {
            'dorm_id': self.male_dorm.id,
            'room_id': self.room.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("جنسیت شما با محدودیت خوابگاه مطابقت ندارد.", response.json().get('non_field_errors', [''])[0])
