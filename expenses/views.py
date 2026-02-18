from datetime import datetime
from django.shortcuts import render
from rest_framework import viewsets, status 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category, Transaction
from .serializers import CategorySerializer, TransactionSerializer
from django.db.models import Sum , Count, Avg



# Create your views here.

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-date')
    serializer_class = TransactionSerializer


@api_view(['GET'])
def transaction_summary(request):
        income_transactions=Transaction.objects.filter(category__name="Income")
        total_income=income_transactions.aggregate(Sum('amount'))['amount__sum'] or 0

        expense_transactions=Transaction.objects.exclude(category__name="Income")
        total_expenses=expense_transactions.aggregate(Sum('amount'))['amount__sum'] or 0

        balance=total_income - total_expenses

        by_category=Transaction.objects.values('category__name').annotate(total=Sum('amount'))

        return Response({
            'total_income': total_income,
            'total_expense':total_expenses,
            'balance' :balance,
            'by_category' : by_category
        })


      
@api_view(['GET'])
def category_stats(request):
      stats=(
            Transaction.objects.values('category__name')
            .annotate(
                count=Count('id'),
                total=Sum('amount'),
                average=Avg('amount')
            )
      )
      return Response(list(stats))

@api_view(['GET'])
def transaction_filter(request):
    qs=Transaction.objects.all()
    category=request.GET.get('category', None)
    min_amount=request.GET.get('min_amount', None)
    max_amount=request.GET.get('max_amount',None)
    start_date=request.GET.get('start_date', None)
    end_date=request.GET.get('end_date',None)
    ordering=request.GET.get('ordering', None)

    try:
        if category:
            qs =qs.filter(category__name=category)
        if min_amount:
            try:
                min_amount=float(min_amount)
                qs=qs.filter(amount__gte=min_amount)
            except ValueError:
                return Response({'error': 'Invalid min_amount value'}, status=status.HTTP_400_BAD_REQUEST)
        if max_amount:
            try:
                max_amount=float(max_amount)
                qs=qs.filter(amount__lte=max_amount)
            except ValueError:
                return Response({'error': 'Invalid max_amount value'}, status=status.HTTP_400_BAD_REQUEST)
            qs=qs.filter(amount__lte=max_amount)
        if start_date and end_date:
            try:
                start_date=datetime.fromisoformat(start_date)
                end_date=datetime.fromisoformat(end_date)
                qs=qs.filter(date__gte=start_date, date__lte=end_date)
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
         

        if ordering:
            allowed_fields=['amount', '-amount', 'date', '-date']
            if ordering not in allowed_fields:
                return Response({'error': f'Invalid ordering field. Allowed fields: {allowed_fields}'}, status=status.HTTP_400_BAD_REQUEST)
            qs=qs.order_by(ordering)


        #stats

        total=qs.aggregate(Sum('amount'))['amount__sum'] or 0
        count=qs.count()
        average=qs.aggregate(Avg('amount'))['amount__avg'] or 0

        serializer=TransactionSerializer(qs, many=True)

        return Response({
            'count': count,
            'total': total,
            'average': average,
            'transactions':serializer.data
    })

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)