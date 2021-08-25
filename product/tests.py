from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

from .models import Product, Order
from .signals import STATUS_CHANGED_NOTIFICATION_EMAIL_TEMPLATE


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

    def setUp(self) -> None:
        self.product_pk = Product.objects.last().pk

    def test_list_product(self) -> None:
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_products = self.product_json(Product.objects.all())
        self.assertListEqual(response.data, expected_products)

    def test_retrieve_product(self) -> None:
        response = self.client.get(
            reverse("product-detail", kwargs={"pk": self.product_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_product = self.product_json(Product.objects.get(pk=self.product_pk))
        self.assertDictEqual(response.data, expected_product)


class OrderTest(APITestCase):
    fixtures = (
        "product/fixtures/orders.json",
        "product/fixtures/order_details.json",
        "product/fixtures/products.json",
        "product/fixtures/users.json",
    )

    @staticmethod
    def order_json(object):
        if isinstance(object, Order):
            return {
                "id": object.id,
                "order_details": [
                    {
                        "product": {
                            "id": order_detail.product.id,
                            "name": order_detail.product.name,
                            "price": order_detail.product.price,
                        },
                        "chosen_option": order_detail.chosen_option,
                    }
                    for order_detail in object.orderdetail_set.all()
                ],
                "status": object.status,
                "total_price": object.total_price,
            }
        else:
            data = []
            for order in object:
                order_data = {
                    "id": order.id,
                    "order_details": [
                        {
                            "product": {
                                "id": order_detail.product.id,
                                "name": order_detail.product.name,
                                "price": order_detail.product.price,
                            },
                            "chosen_option": order_detail.chosen_option,
                        }
                        for order_detail in order.orderdetail_set.all()
                    ],
                    "status": order.status,
                    "total_price": order.total_price,
                }
                data.append(order_data)
            return data

    def setUp(self) -> None:
        self.anonymous_client = APIClient()

        self.user = get_user_model().objects.get(pk=2)
        self.client.force_authenticate(user=self.user)

        self.order_pk = Order.objects.filter(user=self.user, status="W").first().pk
        self.none_waiting_order_pk = (
            Order.objects.filter(user=self.user).exclude(status="W").first().pk
        )

    def test_list_order(self):
        response = self.client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_orders = self.order_json(Order.objects.filter(user=self.user.id))
        self.assertListEqual(response.data, expected_orders)

    def test_anonymous_client_list_order(self):
        response = self.anonymous_client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_order(self):
        response = self.client.get(
            reverse("order-detail", kwargs={"pk": self.order_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_order = self.order_json(
            Order.objects.get(user=self.user.id, pk=self.order_pk)
        )
        self.assertDictEqual(response.data, expected_order)

    def test_anonymous_client_retrieve_order(self):
        response = self.anonymous_client.get(
            reverse("order-detail", kwargs={"pk": self.order_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order(self):
        response = self.client.post(
            reverse("order-list"),
            data={
                "order_details": [
                    {"product": {"id": 1}},
                    {"product": {"id": 2}, "chosen_option": {"milk": 2}},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected_order = self.order_json(Order.objects.last())
        self.assertDictEqual(response.data, expected_order)

    def test_create_order_with_empty_products(self):
        response = self.client.post(
            reverse("order-list"),
            data={"order_details": []},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_invalid_products(self):
        response = self.client.post(
            reverse("order-list"),
            data={
                "order_details": [
                    {"product": {"id": 1000000}},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_client_create_order(self):
        response = self.anonymous_client.post(
            reverse("order-list"),
            data={"order_details": [{"product": {"id": 1}}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_order(self):
        response = self.client.put(
            reverse("order-detail", kwargs={"pk": self.order_pk}),
            data={
                "order_details": [
                    {"product": {"id": 6}, "chosen_option": {"kind": 1}},
                    {"product": {"id": 5}, "chosen_option": {"size": 2}},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_order = self.order_json(Order.objects.get(pk=self.order_pk))
        self.assertDictEqual(response.data, expected_order)

    def test_update_order_with_empty_products(self):
        response = self.client.put(
            reverse("order-detail", kwargs={"pk": self.order_pk}),
            data={"order_details": []},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_with_invalid_products(self):
        response = self.client.put(
            reverse("order-detail", kwargs={"pk": self.order_pk}),
            data={
                "order_details": [
                    {"product": {"id": 1000000}},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_none_waiting_order(self):
        response = self.client.put(
            reverse("order-detail", kwargs={"pk": self.none_waiting_order_pk}),
            data={
                "order_details": [
                    {"product": {"id": 6}, "chosen_option": {"kind": 1}},
                    {"product": {"id": 5}, "chosen_option": {"size": 2}},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_client_update_order(self):
        response = self.anonymous_client.post(
            reverse("order-detail", kwargs={"pk": self.order_pk}),
            data={"order_details": [{"product": {"id": 1}}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order(self):
        response = self.client.delete(
            reverse("order-detail", kwargs={"pk": self.order_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_none_waiting_order(self):
        response = self.client.delete(
            reverse("order-detail", kwargs={"pk": self.none_waiting_order_pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_send_mail_on_order_status_change(self):
        order = Order.objects.get(pk=self.order_pk)
        order.status = "P"
        order.save()

        self.assertEqual(len(mail.outbox), 1)  # inbox is not empty
        self.assertEqual(mail.outbox[0].subject, "Order status changed")
        self.assertEqual(
            mail.outbox[0].body,
            STATUS_CHANGED_NOTIFICATION_EMAIL_TEMPLATE.format(
                order.user.first_name or order.user.username,
                order.pk,
                order.get_status_display(),
            ),
        )
        self.assertEqual(mail.outbox[0].from_email, "webmaster@localhost")
        self.assertListEqual(
            mail.outbox[0].to,
            [
                order.user.email,
            ],
        )
