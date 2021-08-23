from django.contrib import admin

from .models import Product, Order, ProductOrder

# TODO: add filter for admins


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "options")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "get_products")


@admin.register(ProductOrder)
class ProductOrderAdmin(admin.ModelAdmin):
    list_display = ("product", "order", "chosen_options")
