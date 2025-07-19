from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from bookings.models import Booking
from bookings.serializers import BookingCreateSerializer, BookingUpdateSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


class BookingListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
    def get(self, request):
        user = User.objects.filter(id=request.user.id).first()
        if user.is_superuser or user.is_admin:
            bookings = Booking.objects.all()
        else:
            bookings = Booking.objects.filter(student=user)
        serializer = BookingCreateSerializer(bookings, many=True)
        return Response(serializer.data)

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
    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        methods=["GET"],
        summary="دریافت اطلاعات رزرو",
        responses={
            200: OpenApiResponse(
                response=BookingCreateSerializer,
                description="اطلاعات رزرو با موفقیت دریافت شد"
            ),
            404: OpenApiResponse(description="رزرو یافت نشد"),
            401: OpenApiResponse(description="ابتدا وارد شوید")
        },
        parameters=[
            OpenApiParameter(name='booking_id', type=int, description='ID رزرو', required=True)
        ]
    )
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        serializer = BookingCreateSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        methods=["PUT"],
        summary="ویرایش رزرو",
        request=BookingCreateSerializer,
        responses={
            200: OpenApiResponse(
                response=BookingCreateSerializer,
                description="رزرو با موفقیت ویرایش شد"
            ),
            400: OpenApiResponse(description="درخواست نامعتبر"),
            404: OpenApiResponse(description="رزرو یافت نشد"),
            401: OpenApiResponse(description="ابتدا وارد شوید")
        },
        parameters=[
            OpenApiParameter(name='booking_id', type=int, description='ID رزرو', required=True)
        ]
    )
    def put(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        serializer = BookingUpdateSerializer(booking, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        methods=["DELETE"],
        summary="حذف رزرو",
        responses={
            204: OpenApiResponse(description="رزرو با موفقیت حذف شد"),
            404: OpenApiResponse(description="رزرو یافت نشد"),
            401: OpenApiResponse(description="ابتدا وارد شوید")
        },
        parameters=[
            OpenApiParameter(name='booking_id', type=int, description='ID رزرو', required=True)
        ]
    )
    def delete(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        if booking.bed:
            booking.bed.is_occupied = False
            booking.bed.save()
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
