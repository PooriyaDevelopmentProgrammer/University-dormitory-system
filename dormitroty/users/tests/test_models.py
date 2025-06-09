from django.test import TestCase
from users.models import User

class UserModelTest(TestCase):
    """
    Test case for the User model to ensure its functionality.
    """

    def setUp(self):
        self.user = User.objects.create(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            student_code="123456",
            national_code="9876543210",
            phone_number="09123456789",
            gender=User.EnumGender.male,
            is_active=True,
            is_staff=False,
            is_admin=False,
            is_superuser=False,
        )

    def test_user_creation(self):
        """
        Test if the user instance is created correctly.
        """
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertEqual(self.user.student_code, "123456")
        self.assertEqual(self.user.national_code, "9876543210")
        self.assertEqual(self.user.phone_number, "09123456789")
        self.assertEqual(self.user.gender, User.EnumGender.male)
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_admin)
        self.assertFalse(self.user.is_superuser)

    def test_user_string_representation(self):
        """
        Test the string representation of the user instance.
        """
        self.assertEqual(str(self.user), "123456 - 9876543210")

