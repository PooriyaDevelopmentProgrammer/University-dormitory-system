from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from .models import Transaction
from .serializers import TransactionSerializer
from bookings.models import Booking
"""from zeep import Client
from django.conf import settings
from django.shortcuts import get_object_or_404"""
from rest_framework.permissions import IsAdminUser
from dorms.models import Dorm, Bed
from django.db.models import Sum, Count, Q


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


"""
@extend_schema(
    summary="ساخت لینک پرداخت زرین‌پال",
    description="این API یک تراکنش را به درگاه زرین‌پال می‌فرستد و لینک پرداخت ایجاد می‌کند.",
    responses={
        200: OpenApiResponse(
            description="لینک پرداخت با موفقیت ایجاد شد. کاربر باید به آن هدایت شود.",
            examples=[
                {"pay_url": "https://sandbox.zarinpal.com/pg/StartPay/A0000000000000000000000001"}
            ]
        ),
        400: OpenApiResponse(description="تراکنش معتبر یا در وضعیت قابل پرداخت نبود."),
        403: OpenApiResponse(description="دسترسی غیرمجاز به تراکنش"),
    }
)
class StartZarinpalPaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, transaction_id):
        transaction = get_object_or_404(Transaction, id=transaction_id, student=request.user)

        if transaction.status != 'pending':
            return Response({"error": "این تراکنش قبلاً پرداخت شده یا معتبر نیست."},
                            status=status.HTTP_400_BAD_REQUEST)

        client = Client('https://sandbox.zarinpal.com/pg/services/WebGate/wsdl')
        result = client.service.PaymentRequest(
            MerchantID=settings.ZARINPAL_MERCHANT_ID,
            Amount=transaction.amount,
            Description=f"پرداخت رزرو شماره {transaction.booking.id}",
            CallbackURL=settings.ZARINPAL_CALLBACK_URL
        )

        if result.Status == 100:
            pay_url = f"https://sandbox.zarinpal.com/pg/StartPay/{result.Authority}"
            return Response({"pay_url": pay_url})
        else:
            return Response({"error": "خطا در برقراری ارتباط با درگاه پرداخت"},
                            status=status.HTTP_502_BAD_GATEWAY)


@extend_schema(
    summary="تأیید وضعیت پرداخت پس از بازگشت از درگاه",
    description="این endpoint توسط مرورگر کاربر فراخوانی می‌شود پس از پرداخت. اطلاعات از زرین‌پال دریافت و وضعیت تراکنش به روز می‌شود.",
    parameters=[
        OpenApiParameter(name='Authority', type=str, required=True, description='کد Authority دریافتی از درگاه'),
        OpenApiParameter(name='Status', type=str, required=True, description='وضعیت پرداخت (باید OK باشد)'),
    ],
    responses={
        200: OpenApiResponse(description="پرداخت با موفقیت تأیید شد."),
        400: OpenApiResponse(description="پرداخت لغو شده یا معتبر نیست."),
        404: OpenApiResponse(description="تراکنش یافت نشد یا معتبر نیست."),
    }
)
class ZarinpalVerifyAPIView(APIView):
    def get(self, request):
        authority = request.GET.get('Authority')
        status_param = request.GET.get('Status')

        if not authority or status_param != 'OK':
            return Response({'detail': 'پرداخت لغو یا ناقص بود.'}, status=status.HTTP_400_BAD_REQUEST)

        transaction = Transaction.objects.filter(status='pending').order_by('-created_at').first()
        if not transaction:
            return Response({'detail': 'تراکنش معتبر یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        client = Client('https://sandbox.zarinpal.com/pg/services/WebGate/wsdl')
        result = client.service.PaymentVerification(
            MerchantID=settings.ZARINPAL_MERCHANT_ID,
            Authority=authority,
            Amount=transaction.amount
        )

        if result.Status == 100:
            transaction.mark_as_paid(ref_id=result.RefID)

            return Response({'detail': 'پرداخت با موفقیت انجام شد.', 'ref_id': result.RefID})
        else:
            return Response({'detail': 'پرداخت تأیید نشد.', 'status_code': result.Status},
                            status=status.HTTP_400_BAD_REQUEST)
"""


@extend_schema(
    summary="گزارش کامل مالی و ظرفیت خوابگاه‌ها برای مدیر",
    description="این API به مدیر اطلاعات مالی و ظرفیت تخت‌های هر خوابگاه را نمایش می‌دهد.",
    parameters=[
        OpenApiParameter(name='from_date', required=False, type=str, description='تاریخ شروع YYYY-MM-DD'),
        OpenApiParameter(name='to_date', required=False, type=str, description='تاریخ پایان YYYY-MM-DD'),
    ],
    responses={
        200: OpenApiResponse(description="گزارش کامل هر خوابگاه")
    }
)
class DormitoryFullFinanceReportAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        dorms = Dorm.objects.all()
        result = []

        for dorm in dorms:
            transactions = Transaction.objects.filter(
                status='paid',
                booking__room__dorm=dorm
            )

            if from_date:
                transactions = transactions.filter(created_at__gte=from_date)
            if to_date:
                transactions = transactions.filter(created_at__lte=to_date)

            total_income = transactions.aggregate(total=Sum('amount'))['total'] or 0
            total_transactions = transactions.count()

            student_names = list(
                transactions.values_list('student__first_name', 'student__last_name')
                .distinct()
            )
            students = [f"{f} {l}" for f, l in student_names]

            total_rooms = dorm.rooms.count()
            total_capacity = dorm.rooms.aggregate(capacity=Sum('capacity'))['capacity'] or 0
            total_beds = Bed.objects.filter(room__dorm=dorm).count()
            used_beds = Bed.objects.filter(room__dorm=dorm, is_occupied=True).count()
            empty_beds = total_beds - used_beds

            result.append({
                'dorm_name': dorm.name,
                'total_income': total_income,
                'total_transactions': total_transactions,
                'students': students,
                'total_rooms': total_rooms,
                'total_capacity': total_capacity,
                'total_beds': total_beds,
                'used_beds': used_beds,
                'empty_beds': empty_beds,
            })

        return Response(result, status=status.HTTP_200_OK)
