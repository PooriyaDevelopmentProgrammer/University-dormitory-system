from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'student', 'booking', 'amount',
            'status', 'gateway', 'ref_id',
            'description', 'created_at'
        ]
        read_only_fields = ['student', 'amount', 'status', 'ref_id', 'created_at']
