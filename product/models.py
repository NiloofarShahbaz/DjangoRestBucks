from django.db import models
from django.conf import settings


def get_default_product_options():
    return {"consume location": ["take away", "in shop"]}


def get_default_order_option():
    return {"consume location": 0}


class Product(models.Model):
    name = models.CharField(max_length=150)
    price = models.PositiveIntegerField()
    options = models.JSONField(default=get_default_product_options)

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    STATUS_CHOICES = (
        ("W", "Waiting"),
        ("P", "Preparation"),
        ("R", "Ready"),
        ("D", "Delivered"),
    )

    products = models.ManyToManyField(Product, through="product.OrderDetail")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="W")

    def __str__(self) -> str:
        return f"{self.user}-{self.product_list()}"

    def product_list(self) -> str:
        """
        Returns a string of all product names seperated by comma.

        :return str: products
        """
        return ", ".join([product.name for product in self.products.all()])

    @property
    def total_price(self) -> int:
        """
        Returns the total price of ordered products.

        :return int: total_price
        """
        return self.products.aggregate(models.Sum("price")).get("price__sum")


class OrderDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    chosen_option = models.JSONField(default=get_default_order_option)

    def __str__(self):
        return f"{self.product}-{self.order.user}"
