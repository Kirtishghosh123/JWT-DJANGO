from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Role(models.Model):
    objects = models.Manager()
    role = models.CharField(max_length=120)
    permissions = models.JSONField()

    def __str__(self):
        return self.role

class CustomUser(User):
    roles = models.ManyToManyField(Role)

class Category(models.Model):
    objects = models.Manager()
    category_name = models.CharField(max_length=120)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.category_name

class Product(models.Model):
    DoesNotExist = None
    objects = models.Manager()
    product_name = models.CharField(max_length=120)
    description = models.TextField()
    price = models.FloatField(default=0.0)
    stock_quantity = models.IntegerField()
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name + " " + str(self.id)

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_amount = models.FloatField(default=0.0)
    objects = models.Manager()

class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    objects = models.Manager()

class Order(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_amount = models.FloatField(default=0.0)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length = 20)

