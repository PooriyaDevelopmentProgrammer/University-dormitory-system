from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, password=None, **kwargs):
        student_code = kwargs.get('student_code', None)
        national_code = kwargs.get('national_code', None)
        phone_number = kwargs.get('phone_number', None)
        if not student_code:
            raise ValueError("An username is required.")
        if not national_code:
            raise ValueError("A national code is required.")
        if not phone_number:
            raise ValueError("A phone number is required.")
        user = self.model(
            student_code=student_code,
            national_code=national_code,
            phone_number=phone_number,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, password, **kwargs):
        student_code = kwargs.get('student_code', None)
        national_code = kwargs.get('national_code', None)
        phone_number = kwargs.get('phone_number', None)

        user = self.model(
            student_code=student_code,
            national_code=national_code,
            phone_number=phone_number,
        )
        user.set_password(password)
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user
