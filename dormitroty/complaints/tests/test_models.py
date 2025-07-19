from django.test import TestCase
from django.contrib.auth import get_user_model
from complaints.models import Complaint, ComplaintMessage

User = get_user_model()

class ComplaintModelTest(TestCase):
    def setUp(self):
        # Create a test user with email
        self.student = User.objects.create_user(
            email="student@example.com",
            student_code="12345",
            national_code="987654321",
            phone_number="1234567890",
            password="password123"
        )

    def test_create_complaint(self):
        # Create a complaint
        complaint = Complaint.objects.create(
            student=self.student,
            title="Test Complaint",
            is_read=False
        )
        self.assertEqual(complaint.title, "Test Complaint")
        self.assertEqual(complaint.student, self.student)
        self.assertFalse(complaint.is_read)
        self.assertIsNotNone(complaint.created_at)

    def test_complaint_str(self):
        # Test the string representation of a complaint
        complaint = Complaint.objects.create(
            student=self.student,
            title="Test Complaint"
        )
        self.assertEqual(str(complaint), f"Test Complaint - {self.student.student_code}")


class ComplaintMessageModelTest(TestCase):
    def setUp(self):
        # Create test users with email
        self.student = User.objects.create_user(
            email="student@example.com",
            student_code="12345",
            national_code="987654321",
            phone_number="1234567890",
            password="password123"
        )
        self.sender = User.objects.create_user(
            email="sender@example.com",
            student_code="67890",
            national_code="123456789",
            phone_number="0987654321",
            password="password456"
        )

        # Create a complaint
        self.complaint = Complaint.objects.create(
            student=self.student,
            title="Test Complaint"
        )

    def test_create_complaint_message(self):
        # Create a complaint message
        message = ComplaintMessage.objects.create(
            complaint=self.complaint,
            sender=self.sender,
            message="This is a test message."
        )
        self.assertEqual(message.complaint, self.complaint)
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.message, "This is a test message.")
        self.assertIsNotNone(message.created_at)

    def test_complaint_message_str(self):
        # Test the string representation of a complaint message
        message = ComplaintMessage.objects.create(
            complaint=self.complaint,
            sender=self.sender,
            message="This is a test message."
        )
        self.assertEqual(
            str(message),
            f"Msg by {self.sender.student_code} on {message.created_at.strftime('%Y-%m-%d')}"
        )