from rest_framework import serializers
from .models import Category, Expense

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ExpenseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  #Just for reading
    category_id=serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source ='category',
        write_only=True
    )
    class Meta:
        model = Expense
        fields = ['id', 'amount', 'description', 'date', 'category', 'category_id']
