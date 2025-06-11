from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dorms.models import Dorm, Room, Bed
from dorms.serializers import DormSerializer, RoomSerializer, BedSerializer
from drf_spectacular.utils import extend_schema
from rest_framework import permissions


class DormAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @extend_schema(
        summary="List Dorms",
        responses={
            200: DormSerializer(many=True),
            400: "Bad Request",
            401: "Unauthorized",
        }
    )
    def get(self, request):
        dorms = Dorm.objects.all()
        serializer = DormSerializer(dorms, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create Dorm",
        request=DormSerializer,
        responses={
            201: DormSerializer,
            400: "Bad Request",
            401: "Unauthorized",
        }
    )
    def post(self, request):
        serializer = DormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @extend_schema(
        summary="List Rooms",
        responses={
            200: RoomSerializer(many=True),
            400: "Bad Request",
            401: "Unauthorized",
        }
    )
    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create Room",
        request=RoomSerializer,
        responses={
            201: RoomSerializer,
            400: "Bad Request",
            401: "Unauthorized",
        }
    )
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BedAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        summary="List Beds",
        responses={
            200: BedSerializer(many=True),
            400: "Bad Request",
            401: "Unauthorized",
        }
    )
    def get(self, request):
        beds = Bed.objects.all()
        serializer = BedSerializer(beds, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create Bed",
        request=BedSerializer,
        responses={
            201: BedSerializer,
            400: "Bad Request",
            401: "Unauthorized",
        }
    )
    def post(self, request):
        serializer = BedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
