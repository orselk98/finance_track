from urllib import response
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Expense
from datetime import date

# Create your tests here.

class ExpenseTest(APITestCase):
    def setUp(self):
        self.income_cat=Category.objects.create(name='Income')
        self.needs_cat=Category.objects.create(name='Needs')
        self.wants_cat=Category.objects.create(name='Wants')
        self.savings_cat=Category.objects.create(name='Savings')
        self.expense1 =Expense.objects.create(
            amount= 60.00,
            description="Test Description",
            date='2026-01-01',
            category=self.needs_cat

        )
        self.expense2 =Expense.objects.create(
            amount= 100.00,
            description="Test Description 2",
            date='2026-01-02',
            category=self.wants_cat

        )
        self.expense3 =Expense.objects.create(
            amount= 200.00,
            description="Test Description 3",
            date='2026-01-03',
            category=self.income_cat
        )
    def test_summary_success(self):
        url='/api/expenses/summary/'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_income', response.data)
        self.assertIn('total_expense', response.data)
        self.assertIn('balance', response.data)
        self.assertIn('by_category', response.data)

    def test_summary_calculations(self):
        url='/api/expenses/summary/'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_income'], 200.00)
        self.assertEqual(response.data['total_expense'], 160.00)
        self.assertEqual(response.data['balance'], 40.00)

    def test_summary_empty_database(self):

        Expense.objects.all().delete()
        
        url='/api/expenses/summary/'
        
        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['total_income'],0)
        self.assertEqual(response.data['total_expense'],0)
        self.assertEqual(response.data['balance'],0)
