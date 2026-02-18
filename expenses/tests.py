from urllib import response
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Transaction
from datetime import date

# Create your tests here.

class TransactionTest(APITestCase):
    def setUp(self):
        self.income_cat=Category.objects.create(name='Income')
        self.needs_cat=Category.objects.create(name='Needs')
        self.wants_cat=Category.objects.create(name='Wants')
        self.savings_cat=Category.objects.create(name='Savings')
        self.transaction1 =Transaction.objects.create(
            amount= 60.00,
            description="Test Description",
            date='2026-01-01',
            category=self.needs_cat

        )
        self.transaction2 =Transaction.objects.create(
            amount= 100.00,
            description="Test Description 2",
            date='2026-01-02',
            category=self.wants_cat

        )
        self.transaction3 =Transaction.objects.create(
            amount= 200.00,
            description="Test Description 3",
            date='2026-01-03',
            category=self.income_cat
        )
    def test_summary_success(self):
        url='/api/transactions/summary/'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_income', response.data)
        self.assertIn('total_expense', response.data)
        self.assertIn('balance', response.data)
        self.assertIn('by_category', response.data)

    def test_summary_calculations(self):
        url='/api/transactions/summary/'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_income'], 200.00)
        self.assertEqual(response.data['total_expense'], 160.00)
        self.assertEqual(response.data['balance'], 40.00)

    def test_summary_empty_database(self):

        Transaction.objects.all().delete()
        
        url='/api/transactions/summary/'
        
        response=self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['total_income'],0)
        self.assertEqual(response.data['total_expense'],0)
        self.assertEqual(response.data['balance'],0)

class CategoryStatsTest(APITestCase):
    def setUp(self):
        self.income_cat=Category.objects.create(name='Income')
        self.needs_cat=Category.objects.create(name='Needs')
        self.wants_cat=Category.objects.create(name='Wants')
        self.savings_cat=Category.objects.create(name='Savings')
        self.transaction1 =Transaction.objects.create(
            amount= 60.00,
            description="Test Description",
            date='2026-01-01',
            category=self.needs_cat

        )
        self.transaction2 =Transaction.objects.create(
            amount= 100.00,
            description="Test Description 2",
            date='2026-01-02',
            category=self.wants_cat

        )
        self.transaction3 =Transaction.objects.create(
            amount= 200.00,
            description="Test Description 3",
            date='2026-01-03',
            category=self.income_cat
        )

    def test_category_stats_success(self):
        url='/api/transactions/category-stats/'
        response=self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 3)  # Should have 3 categories

    def test_category_stats_calculations(self):
        url='/api/transactions/category-stats/'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        needs_item = None
        for item in response.data:
            if item['category__name'] == 'Needs':
                needs_item = item
                break
        self.assertEqual(needs_item['count'], 1)
        self.assertEqual(needs_item['total'], 60.00)
        self.assertEqual(needs_item['average'], 60.00)

    def test_category_stats_empty_database(self):
        Transaction.objects.all().delete()
        url='/api/transactions/category-stats/'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

class TransactionFilterTest(APITestCase):
    def setUp(self):
        self.income_cat=Category.objects.create(name='Income')
        self.needs_cat=Category.objects.create(name='Needs')
        self.wants_cat=Category.objects.create(name='Wants')
        self.savings_cat=Category.objects.create(name='Savings')
        self.transaction1 =Transaction.objects.create(
            amount= 60.00,
            description="Test Description",
            date='2026-01-01',
            category=self.needs_cat

        )
        self.transaction2 =Transaction.objects.create(
            amount= 100.00,
            description="Test Description 2",
            date='2026-01-02',
            category=self.wants_cat

        )
        self.transaction3 =Transaction.objects.create(
            amount= 200.00,
            description="Test Description 3",
            date='2026-01-03',
            category=self.income_cat
        )

    def test_transaction_filter_category(self):
        url='/api/transactions/filter/?category=Needs'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['transactions']), 1)
        self.assertEqual(response.data['transactions'][0]['category']['name'], 'Needs')

    def test_filter_by_min_amount(self):
        url='/api/transactions/filter/?min_amount=80'
        response=self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        