from django.db import models
from django.conf import settings
from bookings.models import Booking


class Transaction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'در انتظار پرداخت'
        PAID = 'paid', 'پرداخت شده'
        FAILED = 'failed', 'ناموفق'

    class Gateway(models.TextChoices):
        ZARINPAL = 'zarinpal', 'زرین‌پال'
        IDPAY = 'idpay', 'IDPay'
        PAYIR = 'payir', 'Pay.ir'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    amount = models.PositiveIntegerField(help_text="مبلغ به تومان")
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )

    gateway = models.CharField(
        max_length=20,
        choices=Gateway.choices,
        blank=True,
        null=True,
        help_text="درگاه پرداخت انتخابی"
    )

    ref_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="کد پیگیری پرداخت موفق"
    )

    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.student_code} - {self.amount} تومان - {self.status}"

    def mark_as_paid(self, ref_id):
        self.status = self.Status.PAID
        self.ref_id = ref_id
        self.save()
        """
        self.booking.status = self.booking.BookingStatus.APPROVED
        self.booking.save()
        """
