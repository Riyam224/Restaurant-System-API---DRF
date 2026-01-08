from django.shortcuts import render

# Create your views here.
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)

from .serializers import RegisterSerializer


@extend_schema(
    tags=["Accounts"],
    security=[],
    request=RegisterSerializer,
    responses={
        201: RegisterSerializer,
        400: OpenApiResponse(description="Validation error"),
    },
    examples=[
        OpenApiExample(
            "Register Request",
            value={
                "username": "chef_ahmed",
                "email": "ahmed@example.com",
                "password": "P@ssw0rd!",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Register Response",
            value={"id": 12, "username": "chef_ahmed", "email": "ahmed@example.com"},
            response_only=True,
        ),
    ],
)
class RegisterAPIView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register
    """

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


@extend_schema(
    tags=["Accounts"],
    security=[],
    request=inline_serializer(
        name="LoginRequest",
        fields={
            "username": serializers.CharField(),
            "password": serializers.CharField(write_only=True),
        },
    ),
    responses={
        200: OpenApiResponse(
            description="JWT token pair",
            examples=[
                OpenApiExample(
                    "Login Response",
                    value={
                        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    },
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(
            description="Invalid credentials",
            examples=[
                OpenApiExample(
                    "Unauthorized",
                    value={"detail": "No active account found with the given credentials"},
                    response_only=True,
                )
            ],
        ),
    },
)
class LoginAPIView(TokenObtainPairView):
    """
    POST /api/v1/auth/login
    """

    permission_classes = [AllowAny]


@extend_schema(
    tags=["Accounts"],
    security=[],
    request=inline_serializer(
        name="RefreshTokenRequest",
        fields={"refresh": serializers.CharField()},
    ),
    responses={
        200: OpenApiResponse(
            description="New access token",
            examples=[
                OpenApiExample(
                    "Refresh Response",
                    value={"access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(
            description="Invalid or expired token",
            examples=[
                OpenApiExample(
                    "Invalid refresh token",
                    value={"detail": "Token is invalid or expired", "code": "token_not_valid"},
                    response_only=True,
                )
            ],
        ),
    },
)
class RefreshTokenAPIView(TokenRefreshView):
    """
    POST /api/v1/auth/refresh
    """

    permission_classes = [AllowAny]


@extend_schema(
    tags=["Accounts"],
    security=[{"BearerAuth": []}],
    responses={
        200: inline_serializer(
            name="ProfileResponse",
            fields={
                "id": serializers.IntegerField(),
                "username": serializers.CharField(),
                "email": serializers.EmailField(),
            },
        ),
        401: OpenApiResponse(
            description="Authentication required",
            examples=[
                OpenApiExample(
                    "Unauthorized",
                    value={"detail": "Authentication credentials were not provided."},
                    response_only=True,
                )
            ],
        ),
    },
)
class ProfileAPIView(generics.RetrieveAPIView):
    """
    GET /api/v1/profile
    """

    permission_classes = [IsAuthenticated]
    serializer_class = RegisterSerializer

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        )
