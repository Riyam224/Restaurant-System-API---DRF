from django.urls import path
from .views import AddressListCreateAPIView, AddressDetailAPIView

urlpatterns = [
    path("addresses/", AddressListCreateAPIView.as_view(), name="address-list"),
    path("addresses/<int:pk>/", AddressDetailAPIView.as_view(), name="address-detail"),
]
