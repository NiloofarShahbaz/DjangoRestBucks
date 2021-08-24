from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.db import transaction
from django.db.utils import IntegrityError

from .models import Product, Order, OrderDetail, get_default_order_option


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "options")


class ProductMainDetailsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ("id", "name", "price")
        read_only_fields = ("name", "price")


class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductMainDetailsSerializer()
    # TODO: replace chosen_option index with the actual string value.

    class Meta:
        model = OrderDetail
        fields = ("product", "chosen_option")


class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, source="orderdetail_set")

    class Meta:
        model = Order
        fields = ("id", "order_details", "status", "total_price")
        read_only_fields = ("status",)

    def create(self, validated_data: dict) -> Order:
        """
        Tries to add products to order model. fails if one of the product ids is not valid.

        """
        order_details_data = validated_data.pop("orderdetail_set")
        try:
            with transaction.atomic():
                instance = Order.objects.create(**validated_data)
                # add the list of products to ProductOrder
                OrderDetail.objects.bulk_create(
                    OrderDetail(
                        product_id=order_detail["product"].get("id"),
                        order_id=instance.id,
                        chosen_option={**get_default_order_option(), **chosen_option}
                        if (chosen_option := order_detail.get("chosen_option"))
                        else get_default_order_option(),
                    )
                    for order_detail in order_details_data
                )
        except IntegrityError:
            raise ValidationError({"products": "product id is not valid."})
        return instance

    def update(self, instance: Order, validated_data: dict) -> Order:
        """
        Deletes all products from order and adds the given products instead.

        """
        order_details_data = validated_data.pop("orderdetail_set")
        try:
            with transaction.atomic():
                # delete all the orders and replace with the new ones.
                OrderDetail.objects.filter(order_id=instance.id).delete()
                OrderDetail.objects.bulk_create(
                    OrderDetail(
                        product_id=order_detail["product"].get("id"),
                        order_id=instance.id,
                        chosen_option={**get_default_order_option(), **chosen_option}
                        if (chosen_option := order_detail.get("chosen_option"))
                        else get_default_order_option(),
                    )
                    for order_detail in order_details_data
                )
        except IntegrityError:
            raise ValidationError({"products": "product id is not valid."})
        return instance
