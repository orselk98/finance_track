from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet, category_stats, expense_summary, expense_filter

router =DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('expenses/summary/',expense_summary, name='expense-summary'),
    path('expenses/category-stats/', category_stats, name='category-stats'),
    path('expenses/filter/',expense_filter,name='expense-filter'),
    path('', include(router.urls)),

]