from django.contrib.auth import authenticate

# from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import PasswordResetOTP
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ForgotPasswordSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    GoogleAuthSerializer,
)
from .services import UserService

# todo - move to utils


@extend_schema(
    tags=["Authentication"],
    request=RegisterSerializer,
    responses={
        201: UserSerializer,
        400: OpenApiResponse(description="Validation error"),
    },
    examples=[
        OpenApiExample(
            "Register Request",
            value={
                "email": "john@example.com",
                "password": "SecurePass123!",
            },
            request_only=True,
        ),
    ],
)
class RegisterAPIView(generics.CreateAPIView):
    """
    Register a new user account with email and password.
    Username is auto-generated from email if not provided.
    """

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "message": "Registration successful",
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Authentication"],
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            description="JWT token pair",
            examples=[
                OpenApiExample(
                    "Login Response",
                    value={
                        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "user": {
                            "id": 1,
                            "username": "john",
                            "email": "john@example.com",
                        },
                    },
                    response_only=True,
                )
            ],
        ),
        401: OpenApiResponse(description="Invalid credentials"),
    },
    examples=[
        OpenApiExample(
            "Login with Email",
            value={"email": "john@example.com", "password": "SecurePass123!"},
            request_only=True,
        ),
    ],
)
class LoginAPIView(APIView):
    """
    Login with email (or username) and password.
    Returns JWT access and refresh tokens.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email_or_username = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Try to find user by email or username
        user = None
        if "@" in email_or_username:
            # It's an email
            try:
                user = User.objects.get(email=email_or_username.lower())
                username = user.username
            except User.DoesNotExist:
                pass
        else:
            # It's a username
            username = email_or_username

        # Authenticate user
        user = authenticate(
            username=username if user is None else user.username, password=password
        )

        if user is None:
            return Response(
                {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            }
        )


@extend_schema(
    tags=["Authentication"],
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
        401: OpenApiResponse(description="Invalid or expired refresh token"),
    },
)
class RefreshTokenAPIView(TokenRefreshView):
    """
    Refresh access token using refresh token.
    """

    permission_classes = [AllowAny]


@extend_schema(
    tags=["User Profile"],
    responses={
        200: UserSerializer,
        401: OpenApiResponse(description="Authentication required"),
    },
)
class ProfileAPIView(APIView):
    """
    Get current authenticated user profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@extend_schema(
    tags=["Password Reset"],
    request=ForgotPasswordSerializer,
    responses={
        200: OpenApiResponse(
            description="OTP sent to email",
            examples=[
                OpenApiExample(
                    "Success Response",
                    value={
                        "message": "Verification code has been sent to your email.",
                        "otp": "123456",
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(description="Email not found"),
    },
    examples=[
        OpenApiExample(
            "Forgot Password Request",
            value={"email": "john@example.com"},
            request_only=True,
        ),
    ],
)
class ForgotPasswordAPIView(APIView):
    """
    Step 1: Request password reset.
    Sends a 6-digit OTP to the user's email.

    Note: In production, send OTP via email service.
    For development, OTP is returned in the response.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        # Create OTP
        otp_obj = PasswordResetOTP.create_otp(user)

        # In production: Send OTP via email
        # send_email(user.email, f"Your password reset code is: {otp_obj.otp}")

        return Response(
            {
                "message": "Verification code has been sent to your email.",
                "otp": otp_obj.otp,  # Remove this in production!
                "expires_in": "10 minutes",
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Password Reset"],
    request=VerifyOTPSerializer,
    responses={
        200: OpenApiResponse(
            description="OTP verified successfully",
            examples=[
                OpenApiExample(
                    "Success Response",
                    value={
                        "message": "Verification code is valid. You can now reset your password."
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(description="Invalid or expired OTP"),
    },
    examples=[
        OpenApiExample(
            "Verify OTP Request",
            value={"email": "john@example.com", "otp": "123456"},
            request_only=True,
        ),
    ],
)
class VerifyOTPAPIView(APIView):
    """
    Step 2: Verify OTP code.
    Validates the 6-digit code sent to the user's email.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"message": "Verification code is valid. You can now reset your password."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Password Reset"],
    request=ResetPasswordSerializer,
    responses={
        200: OpenApiResponse(
            description="Password reset successful",
            examples=[
                OpenApiExample(
                    "Success Response",
                    value={"message": "Password has been reset successfully."},
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(description="Validation error"),
    },
    examples=[
        OpenApiExample(
            "Reset Password Request",
            value={
                "email": "john@example.com",
                "otp": "123456",
                "new_password": "NewSecurePass123!",
                "confirm_password": "NewSecurePass123!",
            },
            request_only=True,
        ),
    ],
)
class ResetPasswordAPIView(APIView):
    """
    Step 3: Reset password.
    Updates user password after OTP verification.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        otp_obj = serializer.validated_data["otp_obj"]
        new_password = serializer.validated_data["new_password"]

        # Update password
        user.set_password(new_password)
        user.save()

        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()

        return Response(
            {"message": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Authentication"],
    request=GoogleAuthSerializer,
    responses={
        200: OpenApiResponse(
            description="JWT token pair",
            examples=[
                OpenApiExample(
                    "Google Auth Response",
                    value={
                        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "user": {
                            "id": 1,
                            "username": "john",
                            "email": "john@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "avatar": "https://lh3.googleusercontent.com/...",
                            "phone": None,
                            "role": "customer",
                            "is_verified": True
                        },
                        "created": False
                    },
                    response_only=True,
                )
            ],
        ),
        400: OpenApiResponse(description="Invalid Google token"),
    },
    examples=[
        OpenApiExample(
            "Google Auth Request",
            value={
                "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE4MmU0M2NkZGY2N..."
            },
            request_only=True,
        ),
    ],
)
class GoogleAuthAPIView(APIView):
    """
    Authenticate with Google OAuth.

    Send the Google ID token from the frontend Google Sign-In.
    Returns JWT access and refresh tokens.

    **Flow:**
    1. Frontend uses Google Sign-In to get ID token
    2. Frontend sends ID token to this endpoint
    3. Backend verifies token with Google
    4. Backend creates/updates user account
    5. Backend returns JWT tokens for authentication
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Validate the Google ID token
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get verified Google user data
        google_user_data = serializer.validated_data['google_user_data']

        # Create or update user using the service
        user, created = UserService.create_or_update_from_google(google_user_data)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "avatar": user.avatar,
                    "phone": user.phone,
                    "role": user.role,
                    "is_verified": user.is_verified,
                },
                "created": created,
            },
            status=status.HTTP_200_OK
        )
