from django.db import models
from django.conf import settings
from django_jalali.db import models as jalali_models

class Complaint(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = jalali_models.jDateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.student.student_code}"


class ComplaintMessage(models.Model):
    complaint = models.ForeignKey(Complaint, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = jalali_models.jDateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg by {self.sender.student_code} on {self.created_at.strftime('%Y-%m-%d')}"
