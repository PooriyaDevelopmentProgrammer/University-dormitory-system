from django.contrib import admin
from . import models

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('student_code', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    search_fields = ('student_code', 'email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'gender')