from django.shortcuts import render
from rest_framework import viewsets
from .models import Category, Expense
from .serializers import CategorySerializer, ExpenseSerializer

# Create your views here.

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-date')
    serializer_class = ExpenseSerializer
