from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    amount =models.DecimalField(max_digits=7, decimal_places=2)
    description = models.CharField(max_length=100)
    date=models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.description} - {self.amount}"



