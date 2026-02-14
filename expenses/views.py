from django.shortcuts import render
from rest_framework import viewsets 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category, Expense
from .serializers import CategorySerializer, ExpenseSerializer
from django.db.models import Sum , Count, Avg


# Create your views here.

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-date')
    serializer_class = ExpenseSerializer


@api_view(['GET'])
def expense_summary(request):
        income_expenses=Expense.objects.filter(category__name="Income")
        total_income=income_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

        expense_expenses=Expense.objects.exclude(category__name="Income")
        total_expenses=expense_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

        balance=total_income - total_expenses

        by_category=Expense.objects.values('category__name').annotate(total=Sum('amount'))

        return Response({
            'total_income': total_income,
            'total_expense':total_expenses,
            'balance' :balance,
            'by_category' : by_category
        })

      
@api_view(['GET'])
def category_stats(request):
      stats=(
            Expense.objects.values('category__name')
            .annotate(
                  count=Count('id'),
                    total=Sum('amount'),
                    average=Avg('amount')
            )
      )
      return Response(stats)