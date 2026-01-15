from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)

from core.permissions import IsAuthenticatedJWT
from .models import Address
from .serializers import AddressSerializer


@extend_schema(
    tags=["Addresses"],
    summary="List and create addresses",
    description="Get all user addresses or create a new one.",
    responses={
        200: AddressSerializer(many=True),
        201: OpenApiResponse(
            response=AddressSerializer,
            description="Address created",
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
    },
)
class AddressListCreateView(ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticatedJWT]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(
    tags=["Addresses"],
    summary="Get, update, or delete address",
    description="Retrieve, update, or delete a specific address.",
    responses={
        200: AddressSerializer,
        204: OpenApiResponse(description="Address deleted"),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        404: OpenApiResponse(description="Address not found"),
    },
)
class AddressDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticatedJWT]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
