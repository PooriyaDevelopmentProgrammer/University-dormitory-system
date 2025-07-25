from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import MinLengthValidator
from . import managers
from uuid import uuid4


class User(AbstractBaseUser, PermissionsMixin):
    class EnumGender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'

    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    student_code = models.CharField(max_length=20, unique=True)
    national_code = models.CharField(max_length=10, unique=True, validators=[MinLengthValidator(10)])
    phone_number = models.CharField(max_length=15, unique=True, validators=[MinLengthValidator(10)])
    gender = models.CharField(max_length=6, choices=EnumGender.choices, default=EnumGender.MALE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    USERNAME_FIELD = 'student_code'
    REQUIRED_FIELDS = ['national_code', 'phone_number', 'gender']
    objects = managers.UserManager()

    def __str__(self):
        return f'{self.student_code} - {self.national_code}'
