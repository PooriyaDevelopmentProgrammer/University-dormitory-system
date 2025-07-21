from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from bookings.models import Booking
from payments.models import Transaction
from django.urls import reverse
from dorms.models import Dorm, Room, Bed
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class TransactionAPITestCase(APITestCase):
    def setUp(self):
        # Create test users
        self.student = User.objects.create_user(
            email="student@example.com",
            student_code="12345",
            national_code="987654321",
            phone_number="1234567890",
            password="password123"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            student_code="67890",
            national_code="123456789",
            phone_number="0987654321",
            password="adminpassword"
        )

        # Create a dorm and room
        self.dorm = Dorm.objects.create(
            name="Test Dorm",
            location="Test Location",
            gender_restriction="male",
            description="Test Description"
        )
        self.room = Room.objects.create(
            dorm=self.dorm,
            room_number="101",
            capacity=4,
            floor=1,
            price=500000
        )

        # Create a booking
        self.booking = Booking.objects.create(
            student=self.student,
            room=self.room,
            start_date="2023-01-01",
            end_date="2023-01-10"
        )

        # Authenticate the student
        self.client.force_authenticate(user=self.student)

    def test_create_transaction(self):
        # Test creating a transaction
        data = {"booking": self.booking.id}
        response = self.client.post('/api/payments/create/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], self.room.price)

    def test_create_transaction_duplicate(self):
        # Test creating a duplicate transaction
        Transaction.objects.create(
            student=self.student,
            booking=self.booking,
            amount=self.room.price,
            status='pending'
        )
        data = {"booking": self.booking.id}
        response = self.client.post('/api/payments/create/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_transactions(self):
        # Test listing transactions
        Transaction.objects.create(
            student=self.student,
            booking=self.booking,
            amount=self.room.price,
            status='pending'
        )
        response = self.client.get('/api/payments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_transaction(self):
        # Test retrieving a transaction
        transaction = Transaction.objects.create(
            student=self.student,
            booking=self.booking,
            amount=self.room.price,
            status='pending'
        )
        response = self.client.get(f'/api/payments/{transaction.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], self.room.price)

    def test_delete_transaction(self):
        # Test deleting a pending transaction
        transaction = Transaction.objects.create(
            student=self.student,
            booking=self.booking,
            amount=self.room.price,
            status='pending'
        )
        response = self.client.delete(f'/api/payments/{transaction.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_non_pending_transaction(self):
        # Test deleting a non-pending transaction
        transaction = Transaction.objects.create(
            student=self.student,
            booking=self.booking,
            amount=self.room.price,
            status='completed'
        )
        response = self.client.delete(f'/api/payments/{transaction.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permission_denied_for_other_students(self):
        # Test that another student cannot access the transaction
        other_student = User.objects.create_user(
            email="otherstudent@example.com",
            student_code="54322",
            national_code="123456785",
            phone_number="0987654322",
            password="password456"
        )
        transaction = Transaction.objects.create(
            student=self.student,
            booking=self.booking,
            amount=self.room.price,
            status='pending'
        )
        self.client.force_authenticate(user=other_student)
        response = self.client.get(f'/api/payments/{transaction.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DormitoryFinanceReportAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admintest@gmail.com",
            student_code='999999', national_code='9999999999',
            phone_number='09120000000', gender='male',
            is_staff=True, is_admin=True, is_superuser=True
        )
        self.student1 = User.objects.create_user(
            email="student1test@gmail.com",
            student_code='111111', national_code='1111111111',
            phone_number='09111111111', gender='male',
            first_name="علی", last_name="رضایی"

        )
        self.student2 = User.objects.create_user(
            email="student2test@gmail.com",
            student_code='222222', national_code='2222222222',
            phone_number='09112222222', gender='female',
            first_name="مریم", last_name="حسینی"
        )

        self.dorm = Dorm.objects.create(name="Alborz", location="Center", gender_restriction="male")
        self.room = Room.objects.create(dorm=self.dorm, room_number="101", capacity=2, floor=1)
        self.bed1 = Bed.objects.create(room=self.room, bed_number="1", is_occupied=True)
        self.bed2 = Bed.objects.create(room=self.room, bed_number="2", is_occupied=False)

        self.booking1 = Booking.objects.create(student=self.student1, room=self.room, start_date=timezone.now(),
                                               end_date=timezone.now() + timedelta(days=30))
        self.booking2 = Booking.objects.create(student=self.student2, room=self.room, start_date=timezone.now(),
                                               end_date=timezone.now() + timedelta(days=30))

        self.tx1 = Transaction.objects.create(booking=self.booking1, student=self.student1, amount=100000,
                                              status='paid')
        self.tx2 = Transaction.objects.create(booking=self.booking2, student=self.student2, amount=200000,
                                              status='paid')

    def test_only_admin_can_access_report(self):
        # دانشجو نمی‌تونه دسترسی داشته باشه
        self.client.force_authenticate(user=self.student1)
        url = reverse('dormitory-full-report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_see_report(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('dormitory-full-report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), 1)
        report = data[0]
        self.assertEqual(report['dorm_name'], "Alborz")
        self.assertEqual(report['total_income'], 300000)
        self.assertEqual(report['total_transactions'], 2)
        self.assertEqual(report['total_rooms'], 1)
        self.assertEqual(report['total_capacity'], 2)
        self.assertEqual(report['total_beds'], 2)
        self.assertEqual(report['used_beds'], 1)
        self.assertEqual(report['empty_beds'], 1)
        self.assertIn("علی", " ".join(report['students']) or " ".join(report['students']))

    def test_filter_by_date_range(self):
        self.client.force_authenticate(user=self.admin)
        # tx2 رو از 2 روز پیش کنیم تا فیلتر نشه
        self.tx2.created_at = timezone.now() - timedelta(days=2)
        self.tx2.save()

        url = reverse('dormitory-full-report')
        response = self.client.get(url, {'from_date': (timezone.now() - timedelta(days=1)).date().isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        report = data[0]
        self.assertEqual(report['total_income'], 100000)  # فقط tx1 در بازه است
        self.assertEqual(report['total_transactions'], 1)
