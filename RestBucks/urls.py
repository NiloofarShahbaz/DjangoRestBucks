from django.contrib import admin
from django.urls import path, include

from product.urls import urlpatterns as product_urls

api_urls = product_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
]
