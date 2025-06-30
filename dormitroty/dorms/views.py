import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dorms.models import Dorm, Room, Bed
from dorms.serializers import DormSerializer, RoomSerializer, BedSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import permissions


# Python
class DormAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @extend_schema(
        summary="List Dorms",
        parameters=[
            OpenApiParameter(name='name', type=str, description='Filter by dorm name', required=False),
            OpenApiParameter(name='location', type=str, description='Filter by dorm location', required=False),
            OpenApiParameter(name='gender_restriction', type=str, description='Filter by gender restriction',
                             required=False),
        ],
        responses={
            200: DormSerializer(many=True),
            400: "Bad Request",
            401: "Unauthorized",
        }
    )
    def get(self, request):
        dorms = Dorm.objects.all()
        name = request.query_params.get('name')
        location = request.query_params.get('location')
        gender_restriction = request.query_params.get('gender_restriction')

        if name:
            dorms = dorms.filter(name__icontains=name)
        if location:
            dorms = dorms.filter(location__icontains=location)
        if gender_restriction:
            dorms = dorms.filter(gender_restriction=gender_restriction)

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


# Python
class DormDetailsAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        summary="Update Dorm",
        request=DormSerializer,
        responses={
            200: DormSerializer,
            400: "Bad Request",
            404: "Not Found",
            401: "Unauthorized",
        }
    )
    def put(self, request, pk):
        try:
            dorm = Dorm.objects.get(pk=pk)
        except Dorm.DoesNotExist:
            return Response({"detail": "Dorm not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DormSerializer(dorm, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete Dorm",
        responses={
            204: "No Content",
            404: "Not Found",
            401: "Unauthorized",
        }
    )
    def delete(self, request, pk):
        try:
            dorm = Dorm.objects.get(pk=pk)
        except Dorm.DoesNotExist:
            return Response({"detail": "Dorm not found."}, status=status.HTTP_404_NOT_FOUND)

        dorm.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @extend_schema(
        summary="List Rooms",
        parameters=[
            OpenApiParameter(name='dorm_id', description='Filter by dorm ID',
                             required=False, type=uuid.UUID),
            OpenApiParameter(name='floor', description='Filter by floor number',
                             required=False, type=str),
            OpenApiParameter(name='capacity', description='Filter by room capacity',
                             required=False, type=int),
        ],
        responses={
            200: RoomSerializer(many=True),
            400: "Bad Request",
            401: "Unauthorized",
        }
    )
    def get(self, request):
        rooms = Room.objects.all()
        dorm_id = request.query_params.get('dorm_id')
        floor = request.query_params.get('floor')
        capacity = request.query_params.get('capacity')

        if dorm_id:
            rooms = rooms.filter(dorm_id=dorm_id)
        if floor:
            rooms = rooms.filter(floor=floor)
        if capacity:
            rooms = rooms.filter(capacity=capacity)

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
        parameters=[
            OpenApiParameter(name='room_id', description='Filter by room ID',
                             required=False, type=uuid.UUID),
            OpenApiParameter(name='bed_number', description='Filter by bed number',
                             required=False, type=str),
            OpenApiParameter(name='is_occupied',
                             description='Filter by occupancy status', required=False, type=bool),
        ],
        responses={
            200: BedSerializer(many=True),
            400: "Bad Request",
            401: "Unauthorized",
        }
    )
    def get(self, request):
        beds = Bed.objects.all()
        room_id = request.query_params.get('room_id')
        bed_number = request.query_params.get('bed_number')
        is_occupied = request.query_params.get('is_occupied')

        if room_id:
            beds = beds.filter(room_id=room_id)
        if bed_number:
            beds = beds.filter(bed_number=bed_number)
        if is_occupied is not None:
            beds = beds.filter(is_occupied=is_occupied.lower() == 'true')

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
