from rest_framework import serializers
from .models import CreditCard, Transaction

class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = '__all__'
        
    def validate(self, data):
        if data['credit_limit'] < data['current_balance']:
            raise serializers.ValidationError("Current balance cannot exceed credit limit.")
        return data

class TransactionSerializer(serializers.ModelSerializer):
    credit_card = CreditCardSerializer(read_only=True)
    credit_card_id = serializers.PrimaryKeyRelatedField(
        queryset=CreditCard.objects.all(),
        source='credit_card',
        write_only=True,
        required=False
    )
    class Meta:
        model = Transaction
        fields = '__all__'

