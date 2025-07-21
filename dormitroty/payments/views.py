from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Transaction
from .serializers import TransactionSerializer
from bookings.models import Booking


@extend_schema(
    summary="ایجاد تراکنش برای رزرو",
    request=TransactionSerializer,
    responses={
        201: OpenApiResponse(TransactionSerializer),
        400: OpenApiResponse(description="درخواست نامعتبر یا تراکنش تکراری"),
        403: OpenApiResponse(description="رزرو متعلق به شما نیست")
    }
)
class CreateTransactionAPIView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        booking_id = request.data.get('booking')
        if not booking_id:
            raise ValidationError({"booking": "شناسه رزرو الزامی است."})

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            raise ValidationError({"booking": "رزرو یافت نشد."})

        if booking.student != request.user:
            raise PermissionDenied("شما اجازه ثبت تراکنش برای این رزرو را ندارید.")

        if Transaction.objects.filter(booking=booking, status='pending').exists():
            raise ValidationError("شما قبلاً یک تراکنش معلق برای این رزرو ایجاد کرده‌اید.")

        amount = booking.room.price

        transaction = Transaction.objects.create(
            student=request.user,
            booking=booking,
            amount=amount,
            status='pending'
        )
        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransactionListAPIView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="لیست تراکنش‌ها",
        responses={
            200: OpenApiResponse(TransactionSerializer(many=True)),
            401: OpenApiResponse(description="احراز هویت نشده")
        }
    )
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Transaction.objects.all().order_by('-created_at')
        return Transaction.objects.filter(student=user).order_by('-created_at')


class TransactionRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="دریافت اطلاعات یک تراکنش",
        responses={
            200: OpenApiResponse(TransactionSerializer),
            403: OpenApiResponse(description="دسترسی غیرمجاز"),
            404: OpenApiResponse(description="تراکنش یافت نشد")
        }
    )
    def get_object(self):
        try:
            transaction = Transaction.objects.get(pk=self.kwargs['pk'])
        except Transaction.DoesNotExist:
            raise NotFound("تراکنش یافت نشد.")

        user = self.request.user
        if not (user.is_staff or user.is_superuser or transaction.student == user):
            raise PermissionDenied("شما به این تراکنش دسترسی ندارید.")

        return transaction


class TransactionDeleteAPIView(generics.DestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="حذف تراکنش معلق",
        responses={
            204: OpenApiResponse(description="حذف با موفقیت انجام شد"),
            403: OpenApiResponse(description="شما مجاز به حذف این تراکنش نیستید"),
            404: OpenApiResponse(description="تراکنش یافت نشد")
        }
    )
    def get_object(self):
        try:
            transaction = Transaction.objects.get(pk=self.kwargs['pk'])
        except Transaction.DoesNotExist:
            raise NotFound("تراکنش یافت نشد.")

        if transaction.student != self.request.user:
            raise PermissionDenied("شما مجاز به حذف این تراکنش نیستید.")

        if transaction.status != 'pending':
            raise PermissionDenied("فقط تراکنش‌های معلق را می‌توانید حذف کنید.")

        return transaction