from django.db import models
from django.conf import settings
from django.db import models

class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Product(TimeStampMixin):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/')
    def __str__(self):
        return self.name

class Category(TimeStampMixin):
    name = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.name

class OrderShipment(TimeStampMixin):
    address = models.TextField()
    phone = models.CharField(max_length=20)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.JSONField(default=list)
    def __str__(self):
        return f"Order for {self.user.username}"
    def total_price(self):
        return sum(item['total'] for item in self.items) if self.items else 0