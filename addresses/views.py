from django.db.models.deletion import ProtectedError
from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from core.permissions import IsAuthenticatedJWT
from .models import Address
from .serializers import AddressSerializer


# --------------------------------------------------
# ADDRESS LIST + CREATE
# --------------------------------------------------
@extend_schema(
    tags=["Addresses"],
    summary="List my addresses",
    description="Authenticated endpoint. Returns the current user's addresses.",
    responses={
        200: AddressSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
    },
    examples=[
        OpenApiExample(
            "Address List Response",
            value=[
                {
                    "id": 1,
                    "label": "Home",
                    "city": "Riyadh",
                    "street": "King Fahd Rd",
                    "building": "12B",
                    "lat": "24.713552",
                    "lng": "46.675296",
                    "created_at": "2026-01-14T12:30:00Z",
                }
            ],
            response_only=True,
        )
    ],
)
class AddressListCreateAPIView(generics.ListCreateAPIView):
    """
    Private API (JWT)
    Lists and creates addresses for the authenticated user.
    """

    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticatedJWT]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --------------------------------------------------
# ADDRESS DETAIL
# --------------------------------------------------
@extend_schema(
    tags=["Addresses"],
    summary="Retrieve, update, or delete an address",
    parameters=[
        OpenApiParameter(
            name="pk",
            type=int,
            location=OpenApiParameter.PATH,
            description="Address ID",
        )
    ],
    responses={
        200: AddressSerializer,
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        404: OpenApiResponse(description="Address not found"),
    },
)
class AddressDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Private API (JWT)
    Retrieves, updates, or deletes an address for the authenticated user.
    """

    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticatedJWT]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {"detail": "Address is linked to an order and cannot be deleted."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
