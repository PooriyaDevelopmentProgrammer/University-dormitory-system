from math import floor

from rest_framework import serializers
from dorms.models import Dorm, Room, Bed
from django.db.models import Q


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
        fields = ['id', 'capacity', 'floor', 'dorm', 'beds']

    def create(self, validated_data):
        floor = validated_data.pop('floor')
        room_numbers = Room.objects.filter(Q(dorm=validated_data['dorm'])
                                           & Q(floor=floor)).values_list('room_number', flat=True)
        if room_numbers:
            room_numbers = list(map(lambda x: int(x), room_numbers))
            room_numbers.sort()
            highest_room_number = room_numbers[-1]
            room_number = str(highest_room_number + 1)
        else:
            room_number = f'{floor}01'
        room = Room.objects.create(room_number=room_number, floor=floor, **validated_data)
        return room


class DormSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = Dorm
        fields = ['id', 'name', 'location', 'gender_restriction', 'description', 'rooms']
