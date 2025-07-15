from rest_framework import serializers
from bookings.models import Booking
from dorms.models import Room

class BookingCreateSerializer(serializers.ModelSerializer):
    dorm_id = serializers.IntegerField(write_only=True)
    room_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
        extra_kwargs = {
            'student':{'required': False},
        }

    def validate(self, data):
        dorm_id = data.get('dorm_id')
        room_id = data.get('room_id')

        try:
            room = Room.objects.get(id=room_id, dorm_id=dorm_id)
        except Room.DoesNotExist:
            raise serializers.ValidationError("اتاق انتخاب‌شده در این خوابگاه وجود ندارد.")

        # در صورت نیاز: بررسی اینکه اتاق پر نباشه
        if room.full:
            raise serializers.ValidationError("ظرفیت این اتاق تکمیل شده است.")

        data['room'] = room
        return data

    def create(self, validated_data):
        student = self.context['request'].user
        room = validated_data['room']

        return Booking.objects.create(
            student=student,
            room=room,
            status=Booking.BookingStatus.PENDING
        )
