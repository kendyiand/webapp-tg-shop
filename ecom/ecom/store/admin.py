from django.contrib import admin
from .models import Category, User, Product, Order

admin.site.register(Category)
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Order)

