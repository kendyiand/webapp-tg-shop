from django.db import models
import datetime


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class Product(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.IntegerField()
    sku = models.CharField(max_length=9)
    file_id = models.CharField(max_length=50)
    # image = models.ImageField(upload_to='uploads/product/', default='uploads/product/AgACAgIAAxkBAAIK02UiuKzQ-VDRQKrq6BylDvUw8hlaAAIbzzEb6NwRSSz-TCtBgE6vAQADAgADeAADMAQ.png')

    class Meta:
        managed = False
        # db_table = 'Product'
        # app_label = 'store'
        db_table = 'shopdatabase.Product'


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    user_role = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Order(models.Model):
    date = models.DateField(default=datetime.datetime.today)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.product
