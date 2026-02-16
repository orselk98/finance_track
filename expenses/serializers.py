from rest_framework import serializers
from .models import Category, Transaction

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TransactionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  #Just for reading
    category_id=serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source ='category',
        write_only=True
    )
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'description', 'date', 'category', 'category_id']
