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
            'student': {'required': False},
        }

    def validate(self, data):
        dorm_id = data.get('dorm_id')
        room_id = data.get('room_id')
        user = self.context['request'].user

        try:
            room = Room.objects.get(id=room_id, dorm_id=dorm_id)
        except Room.DoesNotExist:
            raise serializers.ValidationError("اتاق انتخاب‌شده در این خوابگاه وجود ندارد.")

        # در صورت نیاز: بررسی اینکه اتاق پر نباشه
        if room.full:
            raise serializers.ValidationError("ظرفیت این اتاق تکمیل شده است.")

        dorm_gender = room.dorm.gender_restriction
        if dorm_gender != user.gender:
            raise serializers.ValidationError("جنسیت شما با محدودیت خوابگاه مطابقت ندارد.")

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


class BookingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['status', 'rejection_reason', 'bed', 'start_date', 'end_date']

    def validate(self, data):
        if data.get('status') == Booking.BookingStatus.REJECTED and not data.get('rejection_reason'):
            raise serializers.ValidationError("لطفاً دلیل رد درخواست را وارد کنید.")
        elif data.get('status') == Booking.BookingStatus.APPROVED and not data.get('bed'):
            raise serializers.ValidationError("لطفاً تخت مورد نظر را انتخاب کنید.")
        return data

    def update(self, instance, validated_data):
        new_bed = validated_data.get('bed')
        if new_bed:
            new_bed.is_occupied = True
            new_bed.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
