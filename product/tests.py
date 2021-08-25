from rest_framework import status
from rest_framework.test import APITestCase

from django.urls import reverse

from .models import Product


class ProductTest(APITestCase):
    fixtures = ("product/fixtures/products.json",)

    @staticmethod
    def product_json(object):
        if isinstance(object, Product):
            return {
                "id": object.id,
                "name": object.name,
                "price": object.price,
                "options": object.options,
            }
        else:
            data = []
            for product in object:
                product_data = {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "options": product.options,
                }
                data.append(product_data)
            return data

    def setUp(self):
        self.product_pk = Product.objects.last().pk

    def test_list_products(self):
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_products = self.product_json(Product.objects.all())
        self.assertListEqual(response.data, expected_products)

    def test_retrieve_product(self):
        response = self.client.get(
            reverse("product-detail", kwargs={"pk": self.product_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_product = self.product_json(Product.objects.get(pk=self.product_pk))
        self.assertDictEqual(response.data, expected_product)
