from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('is_active', 'is_staff', 'is_admin', 'is_superuser')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if 'phone_number' in data:
            if data['phone_number'].startswith('+98'):
                data['phone_number'] = '0' + data['phone_number'][3:]
            elif data['phone_number'].startswith('9'):
                data['phone_number'] = '0' + data['phone_number']
            else:
                if not data['phone_number'].startswith('0'):
                    raise serializers.ValidationError("Phone number must start with 0 or 9.")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


