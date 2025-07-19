from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Complaint, ComplaintMessage
from .serializers import ComplaintSerializer, ComplaintMessageSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    summary="لیست یا ثبت شکایت",
    description="""
    - اگر کاربر ادمین باشد، تمام شکایات را می‌بیند.
    - اگر دانشجو باشد، فقط شکایات خودش را می‌بیند.
    - با POST شکایت جدید ثبت می‌شود.
    """,
    responses={
        200: OpenApiResponse(response=ComplaintSerializer(many=True), description="لیست شکایات"),
        201: OpenApiResponse(response=ComplaintSerializer, description="شکایت جدید ایجاد شد"),
        401: OpenApiResponse(description="احراز هویت نشده"),
    },
    request=ComplaintSerializer
)
class ComplaintListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Complaint.objects.all().order_by('-created_at')
        return Complaint.objects.filter(student=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


@extend_schema(
    summary="ارسال پیام در یک شکایت",
    description="""
    ارسال پیام جدید در شکایت مشخص‌شده.
    فقط دانشجوی صاحب شکایت یا مدیر می‌توانند پیام ارسال کنند.
    """,
    request=ComplaintMessageSerializer,
    responses={
        201: OpenApiResponse(response=ComplaintMessageSerializer, description="پیام ارسال شد"),
        403: OpenApiResponse(description="دسترسی غیرمجاز"),
        404: OpenApiResponse(description="شکایت یافت نشد"),
    },
    parameters=[
        OpenApiParameter(name='complaint_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH,
                         description='شناسه شکایت', required=True),
    ]
)
class ComplaintMessageCreateAPIView(generics.CreateAPIView):
    serializer_class = ComplaintMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        complaint_id = self.kwargs['complaint_id']
        complaint = Complaint.objects.get(id=complaint_id)

        if self.request.user != complaint.student and not self.request.user.is_staff:
            raise PermissionDenied("شما مجاز به ارسال پیام در این شکایت نیستید.")

        serializer.save(complaint=complaint, sender=self.request.user)


@extend_schema(
    summary="لیست پیام‌های یک شکایت",
    description="""
    پیام‌های موجود در یک شکایت را لیست می‌کند.
    فقط دانشجوی صاحب شکایت یا مدیر می‌تواند این پیام‌ها را مشاهده کند.
    """,
    responses={
        200: OpenApiResponse(response=ComplaintMessageSerializer(many=True), description="لیست پیام‌ها"),
        403: OpenApiResponse(description="دسترسی غیرمجاز"),
        404: OpenApiResponse(description="شکایت یافت نشد"),
    },
    parameters=[
        OpenApiParameter(name='complaint_id', type=OpenApiTypes.INT, location=OpenApiParameter.PATH,
                         description='شناسه شکایت', required=True),
    ]
)
class ComplaintMessageListAPIView(generics.ListAPIView):
    serializer_class = ComplaintMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        complaint_id = self.kwargs['complaint_id']
        complaint = Complaint.objects.get(id=complaint_id)

        if self.request.user != complaint.student and not self.request.user.is_staff:
            raise PermissionDenied("دسترسی به پیام‌های این شکایت ندارید.")

        return ComplaintMessage.objects.filter(complaint=complaint).order_by('created_at')

@extend_schema(
    summary="حذف یک شکایت (اتاق چت)",
    description="فقط مدیر یا دانشجوی ایجادکننده می‌تواند یک شکایت را حذف کند.",
    parameters=[
        OpenApiParameter(name='pk', location=OpenApiParameter.PATH, type=int, description='شناسه شکایت')
    ],
    responses={
        204: OpenApiResponse(description="با موفقیت حذف شد"),
        403: OpenApiResponse(description="دسترسی غیرمجاز"),
        404: OpenApiResponse(description="شکایت یافت نشد")
    }
)
class ComplaintDeleteAPIView(generics.DestroyAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        user = self.request.user
        if user != instance.student and not user.is_staff:
            raise PermissionDenied("شما مجاز به حذف این شکایت نیستید.")
        instance.delete()

@extend_schema(
    summary="حذف یک پیام",
    description="فقط فرستنده پیام یا مدیر می‌تواند پیام را حذف کند.",
    parameters=[
        OpenApiParameter(name='pk', location=OpenApiParameter.PATH, type=int, description='شناسه پیام')
    ],
    responses={
        204: OpenApiResponse(description="با موفقیت حذف شد"),
        403: OpenApiResponse(description="دسترسی غیرمجاز"),
        404: OpenApiResponse(description="پیام یافت نشد")
    }
)
class ComplaintMessageDeleteAPIView(generics.DestroyAPIView):
    queryset = ComplaintMessage.objects.all()
    serializer_class = ComplaintMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        user = self.request.user
        if user != instance.sender and not user.is_staff:
            raise PermissionDenied("شما مجاز به حذف این پیام نیستید.")
        instance.delete()

@extend_schema(
    summary="ویرایش یک پیام",
    description="فقط فرستنده پیام می‌تواند آن را ویرایش کند.",
    parameters=[
        OpenApiParameter(name='pk', location=OpenApiParameter.PATH, type=int, description='شناسه پیام')
    ],
    request=ComplaintMessageSerializer,
    responses={
        200: OpenApiResponse(response=ComplaintMessageSerializer, description="ویرایش موفق"),
        403: OpenApiResponse(description="دسترسی غیرمجاز"),
        404: OpenApiResponse(description="پیام یافت نشد")
    }
)
class ComplaintMessageUpdateAPIView(generics.UpdateAPIView):
    queryset = ComplaintMessage.objects.all()
    serializer_class = ComplaintMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user
        if user != instance.sender:
            raise PermissionDenied("شما مجاز به ویرایش این پیام نیستید.")
        serializer.save()