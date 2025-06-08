from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from . import managers


class User(AbstractBaseUser, PermissionsMixin):
    class EnumGender(models.TextChoices):
        male = 'male', 'male'
        female = 'female', 'female'

    email = models.EmailField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    student_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    national_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    gender = models.CharField(choices=EnumGender.choices, default=EnumGender.male)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin= models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = 'student_code'
    REQUIRED_FIELDS = ['national_code', 'phone_number', 'gender']
    objects = managers.UserManager()

    def __str__(self):
        return f'{self.student_code} - {self.national_code}'
