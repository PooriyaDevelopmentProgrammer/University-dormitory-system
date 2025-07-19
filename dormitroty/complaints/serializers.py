from rest_framework import serializers
from .models import Complaint, ComplaintMessage


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['id', 'student', 'title', 'is_read', 'created_at']
        read_only_fields = ['student', 'is_read', 'created_at']

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class ComplaintMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = ComplaintMessage
        fields = ['id', 'complaint', 'sender', 'sender_name', 'message', 'created_at']
        read_only_fields = ['sender', 'created_at', 'sender_name']
        extra_kwargs = {
            'complaint': {'required': False},
        }

    def get_sender_name(self, obj):
        return f"{obj.sender.first_name} {obj.sender.last_name}"

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)
