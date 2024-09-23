from django.urls import path
from .views import WixProductListView

urlpatterns = [
    path('wix-products/', WixProductListView.as_view(), name='wix_product_list'),  # This must match exactly
]