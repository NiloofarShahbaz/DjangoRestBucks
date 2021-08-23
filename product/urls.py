from rest_framework import routers

from .views import ProductViewSet, OrderViewSet

router = routers.SimpleRouter()
router.register(r"product", ProductViewSet, basename="product")
router.register(r"order", OrderViewSet, basename="order")
urlpatterns = router.urls
