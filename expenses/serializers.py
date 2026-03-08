from rest_framework import serializers
from .models import CreditCard, Transaction

class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = '__all__'
        
    def validate(self, data):
        credit_limit = data.get('credit_limit', getattr(self.instance, 'credit_limit', None))
        current_balance = data.get('current_balance', getattr(self.instance, 'current_balance', None))
        if credit_limit is not None and current_balance is not None and credit_limit < current_balance:
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

