from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import Permission


class UserManager(BaseUserManager):
    def create_user(self, email, student_code, national_code, phone_number, password=None, groups=None,
                    permissions=None, **extra_fields):
        """
        Create and return a regular user with the given required fields and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        if not student_code:
            raise ValueError("The Student Code field must be set")
        if not national_code:
            raise ValueError("The National Code field must be set")
        if not phone_number:
            raise ValueError("The Phone Number field must be set")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            student_code=student_code,
            national_code=national_code,
            phone_number=phone_number,
            **extra_fields
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)

        # Handle many-to-many relationships
        if groups:
            user.groups.set(groups)

        return user

    def create_superuser(self, email, student_code, national_code, phone_number, password=None, groups=None,
                         permissions=None, **extra_fields):
        """
        Create and return a superuser with the given required fields and password.
        """
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_admin'):
            raise ValueError("Superuser must have is_admin=True.")
        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, student_code, national_code, phone_number, password, groups, permissions,
                                **extra_fields)
