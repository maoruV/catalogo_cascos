"""URL configuration for the catalog app."""

from django.urls import path

from catalog.views import ProductDetailView, ProductListView

app_name = "catalog"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
]
