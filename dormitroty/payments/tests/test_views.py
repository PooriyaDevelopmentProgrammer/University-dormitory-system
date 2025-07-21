from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from bookings.models import Booking
from dorms.models import Dorm, Room
from payments.models import Transaction

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