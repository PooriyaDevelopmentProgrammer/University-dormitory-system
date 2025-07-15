from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from bookings.models import Booking
from bookings.serializers import BookingCreateSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from django.contrib.auth import get_user_model
User = get_user_model()

@extend_schema(
    methods=["GET"],
    summary="لیست رزروهای من",
    responses={
        200: OpenApiResponse(
            response=BookingCreateSerializer(many=True),
            description="لیست رزروهای ثبت‌شده توسط کاربر"
        ),
        401: OpenApiResponse(description="first login")

    }
)
@extend_schema(
    methods=["POST"],
    summary="ثبت رزرو جدید",
    request=BookingCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=BookingCreateSerializer,
            description="رزرو جدید با موفقیت ثبت شد"
        ),
        400: OpenApiResponse(description="درخواست نامعتبر (مثلاً اتاق پر است)"),
        401: OpenApiResponse(description="first login")
    },
    parameters=[
        OpenApiParameter(name='dorm_id', type=int, description='ID خوابگاه', required=True),
        OpenApiParameter(name='room_id', type=int, description='ID اتاق', required=True)
    ]
)
class BookingListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = User.objects.filter(id=request.user.id).first()
        if User.is_superuser or User.is_admin:
            bookings = Booking.objects.all()
        else:
            booking = Booking.objects.filter(student=user)
        serializer = BookingCreateSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
