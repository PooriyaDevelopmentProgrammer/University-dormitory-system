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
        self.user = User.objects.create_superuser(**self.user_data)
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class UserDetailsViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            student_code="123456",
            national_code="9876543210",
            phone_number="09123456789",
            gender="male",
            password="testpassword123"
        )
        self.update_data = {
            "first_name": "UpdatedName",
            "last_name": "UpdatedLastName",
            "phone_number": "09129876543",
            "password": "newpassword123"
        }

    def test_update_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(f'/api/users/details/{self.user.id}/', self.update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "UpdatedName")
        self.assertEqual(self.user.last_name, "UpdatedLastName")
        self.assertEqual(self.user.phone_number, "09129876543")
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_delete_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/users/details/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_get_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/users/details/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['student_code'], self.user.student_code)
        self.assertEqual(response.data['national_code'], self.user.national_code)
        self.assertEqual(response.data['phone_number'], self.user.phone_number)


class UserSearchAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            email="test1@example.com",
            student_code="12345",
            national_code="67890",
            phone_number="1234567890",
            gender="male",
            first_name='John',
            last_name='Smith'
        )
        self.user2 = User.objects.create(
            email="test2@example.com",
            student_code="54321",
            national_code="09876",
            phone_number="0987654321",
            gender="female"
        )

        self.admin_user = User.objects.create_superuser(
            email="test3@example.com",
            student_code="54621",
            national_code="123456789",
            phone_number="0987456516",
            gender="female",
            password="adminpassword123"
        )
        self.client = APIClient()
        self.search_url = '/api/users/'

    def test_search_users_by_email(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.search_url, {'email': 'test1@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], "test1@example.com")

    def test_search_users_by_student_code(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.search_url, {'student_code': '54321'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['student_code'], "54321")

    def test_search_users_by_national_code(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.search_url, {'national_code': '67890'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['national_code'], "67890")

    def test_search_users_by_phone_number(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.search_url, {'phone_number': '0987654321'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['phone_number'], "0987654321")

    def test_search_users_by_gender(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.search_url, {'gender': 'male'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['gender'], "male")

    def test_search_users_by_first_name(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.search_url, {'first_name': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], "John")

    def test_search_users_by_last_name(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.search_url, {'last_name': 'Smith'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['last_name'], "Smith")


class ValidatePhoneNumberTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "student_code": "123456",
            "national_code": "9876543210",
            "phone_number": "+989123456789",
            "gender": "male",
            "password": "testpassword123"
        }
        self.invalid_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "student_code": "123456",
            "national_code": "9876543210",
            "phone_number": "8123456789",
            "gender": "male",
            "password": "testpassword123"
        }

    def test_valid_phone_number(self):
        response = self.client.post('/api/users/', self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User created successfully')

    def test_invalid_phone_number(self):
        response = self.client.post('/api/users/', self.invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Phone number must start with 0 or 9.', response.data['non_field_errors'])


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
