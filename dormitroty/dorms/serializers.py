from rest_framework import serializers
from dorms.models import Dorm, Room, Bed


class BedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bed
        fields = ['id', 'bed_number', 'is_occupied', 'room']

    def validate(self, data):
        room = data.get('room')

        if room and room.beds.count() >= room.capacity:
            raise serializers.ValidationError({
                "The number of beds cannot exceed the room's capacity"
            })
        return data


class RoomSerializer(serializers.ModelSerializer):
    beds = BedSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'capacity', 'floor', 'dorm', 'beds']


class DormSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = Dorm
        fields = ['id', 'name', 'location', 'gender_restriction', 'description', 'rooms']