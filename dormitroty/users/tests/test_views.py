from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from users.serializers import UserRegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class UserRegisterViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "student_code": "123456",
            "national_code": "9876543210",
            "phone_number": "09123456789",
            "gender": "male",
            "password": "testpassword123"
        }

    def test_register_user(self):
        response = self.client.post('/api/users/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User created successfully')

    def test_get_all_users(self):
        self.user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class CustomTokenObtainPairViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            student_code="123456",
            national_code='9876543210',
            phone_number='09123456789',
            gender='male',
            password="testpassword123"
        )

    def test_obtain_token(self):
        response = self.client.post('/api/users/token/', {
            "student_code": "123456",
            "password": "testpassword123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class CustomTokenRefreshViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            student_code="123456",
            national_code='9876543210',
            phone_number='09123456789',
            gender='male',
            password="testpassword123"
        )

        self.token = RefreshToken.for_user(self.user)

    def test_refresh_token(self):
        response = self.client.post('/api/users/token/refresh/', {
            "refresh": str(self.token)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

class LogoutViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            student_code="123456",
            national_code='9876543210',
            phone_number='09123456789',
            gender='male',
            password="testpassword123"
        )

        self.token = RefreshToken.for_user(self.user)

    def test_logout_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/users/logout/', {
            "refresh": str(self.token)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Successfully logged out')