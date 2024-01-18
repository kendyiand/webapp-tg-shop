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
    file_id = models.CharField(max_length=100)

    #discount
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'product'

    def __str__(self):
        return self.name


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    user_role = models.CharField(max_length=10)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.first_name


class Order(models.Model):
    date = models.DateField(default=datetime.datetime.today)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.product
