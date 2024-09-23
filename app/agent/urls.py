from django.urls import path
from .views import WixProductListView

urlpatterns = [
    path('wix-products/', WixProductListView.as_view(), name='wix_product_list'),  # URL to view WixProducts and export CSV
]