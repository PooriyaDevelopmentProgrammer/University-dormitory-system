from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from complaints.models import Complaint, ComplaintMessage

User = get_user_model()

class ComplaintAPITestCase(APITestCase):
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

        # Create a complaint
        self.complaint = Complaint.objects.create(
            student=self.student,
            title="Test Complaint"
        )

        # Authentication
        self.client.force_authenticate(user=self.student)
    def test_list_complaints(self):
        # Test listing complaints for a student
        response = self.client.get('/api/complaints/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_complaint(self):
        # Test creating a new complaint
        data = {"title": "New Complaint"}
        response = self.client.post('/api/complaints/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "New Complaint")

    def test_send_message(self):
        # Test sending a message in a complaint
        data = {"message": "This is a test message."}
        response = self.client.post(f'/api/complaints/{self.complaint.id}/messages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "This is a test message.")

    def test_list_messages(self):
        # Test listing messages in a complaint
        ComplaintMessage.objects.create(
            complaint=self.complaint,
            sender=self.student,
            message="Test Message"
        )
        response = self.client.get(f'/api/complaints/{self.complaint.id}/messages/send/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], "Test Message")

    def test_permission_denied_for_other_students(self):
        # Test that another student cannot access the complaint
        other_student = User.objects.create_user(
            email="otherstudent@example.com",
            student_code="54322",
            national_code="123456788",
            phone_number="0987654322",
            password="password456"
        )
        self.client.force_authenticate(user=other_student)
        response = self.client.get(f'/api/complaints/{self.complaint.id}/messages/send/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(f'/api/complaints/{self.complaint.id}/messages/', {"message": "Unauthorized message"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ComplaintMessageAPITests(APITestCase):
    def setUp(self):
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
        self.other = User.objects.create_user(
            email="other@example.com",
            student_code="12343",
            national_code="987654322",
            phone_number="1234567891",
            password="password123"
        )
        # شکایت و پیام
        self.complaint = Complaint.objects.create(student=self.student, title="قطعی برق")
        self.message = ComplaintMessage.objects.create(
            complaint=self.complaint,
            sender=self.student,
            message="برق خوابگاه قطع شده!"
        )
        self.client.force_authenticate(user=self.student)

    def test_student_can_delete_own_complaint(self):
        url = f"/api/complaints/{self.complaint.id}/delete/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_delete_any_complaint(self):
        self.client.force_authenticate(user=self.admin)
        url = f"/api/complaints/{self.complaint.id}/delete/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_delete_complaint(self):
        self.client.force_authenticate(user=self.other)
        url = f"/api/complaints/{self.complaint.id}/delete/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sender_can_delete_own_message(self):
        url = f"/api/complaints/messages/{self.message.id}/delete/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_delete_message(self):
        self.client.force_authenticate(user=self.other)
        url = f"/api/complaints/messages/{self.message.id}/delete/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sender_can_update_own_message(self):
        url = f"/api/complaints/messages/{self.message.id}/update/"
        data = {"message": "پیام ویرایش‌شده"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertEqual(self.message.message, data["message"])

    def test_other_user_cannot_update_message(self):
        self.client.force_authenticate(user=self.other)
        url = f"/api/complaints/messages/{self.message.id}/update/"
        data = {"message": "پیام جعلی"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
