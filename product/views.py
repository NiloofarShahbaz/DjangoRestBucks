from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.filter(user_id=self.request.user.id)
        if self.action not in ("update", "partial_update", "destroy"):
            return queryset.filter(status="W")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)

    # TODO: partial update with action of + or - for addition and exclusion.
    # e.g:
    # {
    #     "action": "+",
    #     "products": [
    #         {
    #             "product": {
    #                 "id": 2
    #             },
    #             "chosen_option": {"milk": 2}
    #         }
    #     ],
    #     "action": "-",
    #     "products": [
    #         {
    #             "product": {
    #                 "id": 1
    #             },
    #             "chosen_option": {"milk": 2}
    #         }
    #     ],
    # }
