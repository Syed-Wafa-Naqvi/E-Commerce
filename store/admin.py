from django.contrib import admin
from .models import Product, Category,OrderShipment

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(OrderShipment)