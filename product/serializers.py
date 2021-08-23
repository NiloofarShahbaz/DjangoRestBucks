from rest_framework import serializers

from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "options")


class ProductWithoutOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "price")


class OrderSerializer(serializers.ModelSerializer):
    products = ProductWithoutOptionsSerializer(many=True)

    class Meta:
        model = Order
        fields = ("id", "products", "status", "total_price")
