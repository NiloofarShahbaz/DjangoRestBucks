from django.db import models
from django.conf import settings


def get_default_product_options():
    return {"consume location": ["take away", "in shop"]}


def get_default_order_options():
    return {"consume location": 0}


class Product(models.Model):
    name = models.CharField(max_length=150)
    price = models.PositiveIntegerField()
    options = models.JSONField(default=get_default_product_options)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = (
        ("W", "Waiting"),
        ("P", "Preparation"),
        ("R", "Ready"),
        ("D", "Delivered"),
    )

    products = models.ManyToManyField(Product, through="product.ProductOrder")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.user}-{self.get_products()}"

    def get_products(self):
        return ", ".join([product.name for product in self.products.all()])


class ProductOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    chosen_options = models.JSONField(default=get_default_order_options)

    def __str__(self):
        return f"{self.product}-{self.order.user}"
