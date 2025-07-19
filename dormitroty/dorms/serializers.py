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

    def create(self, validated_data):
        room = validated_data.get('room')
        validated_data.pop('bed_number')
        bed = Bed.objects.create(**validated_data)
        room.set_full_true()
        room.resequence_beds_for_room()
        return bed


class RoomSerializer(serializers.ModelSerializer):
    beds = BedSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'capacity', 'floor', 'dorm', 'beds', 'price']
        extra_kwargs = {
            'room_number': {'required': False},
            'beds': {'required': False},
        }

    def validate(self, data):
        if 'room_number' in data and not data['room_number']:
            raise serializers.ValidationError({
                "room_number": "This field cannot be blank."
            })
        return data

    def create(self, validated_data):
        floor = validated_data.pop('floor')
        room_numbers = Room.objects.filter(Q(dorm=validated_data['dorm'])
                                           & Q(floor=floor)).values_list('room_number', flat=True)
        if room_numbers:
            room_numbers = list(map(lambda x: int(x), room_numbers))
            room_numbers.sort()
            highest_room_number = room_numbers[-1]
            validated_data['room_number'] = str(highest_room_number + 1)
        else:
            validated_data['room_number'] = f'{floor}01'

        room = Room.objects.create(floor=floor, **validated_data)
        for _ in range(validated_data['capacity']):
            Bed.objects.create(room=room, bed_number=room.beds.count() + 1)

        return room


class DormSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = Dorm
        fields = ['id', 'name', 'location', 'gender_restriction', 'description', 'rooms']
