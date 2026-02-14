# from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import PasswordResetOTP
from django.contrib.auth import get_user_model
from .services import GoogleOAuthService, UserService

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration - matches UI fields"""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    username = serializers.CharField(
        required=False
    )  # Optional, can be generated from email

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "phone", "avatar", "role"]

    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        """Create and return a new user"""
        # If username not provided, generate from email
        if not validated_data.get("username"):
            base_username = validated_data["email"].split("@")[0]
            validated_data["username"] = UserService.generate_unique_username(base_username)
        else:
            # Ensure username is unique
            base_username = validated_data["username"]
            validated_data["username"] = UserService.generate_unique_username(base_username)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login - supports email or username"""

    email = serializers.CharField(required=True, help_text="Email or username")
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "phone", "avatar", "role", "is_verified"]
        read_only_fields = ["id", "is_verified"]


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password request - Step 1: Send OTP"""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Check if email exists"""
        if not User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value.lower()


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for OTP verification - Step 2: Verify code"""

    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6, min_length=6)

    def validate_email(self, value):
        """Check if email exists"""
        if not User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value.lower()

    def validate(self, attrs):
        """Verify OTP is valid"""
        email = attrs.get("email")
        otp = attrs.get("otp")

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError({"email": "User not found."})

        # Get the latest OTP for this user
        otp_obj = PasswordResetOTP.objects.filter(
            user=user, otp=otp, is_used=False
        ).first()

        if not otp_obj:
            raise serializers.ValidationError({"otp": "Invalid verification code."})

        if not otp_obj.is_valid():
            raise serializers.ValidationError({"otp": "Verification code has expired."})

        attrs["otp_obj"] = otp_obj
        attrs["user"] = user
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset - Step 3: Set new password"""

    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate_email(self, value):
        """Check if email exists"""
        if not User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value.lower()

    def validate(self, attrs):
        """Validate passwords match and OTP is valid"""
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        email = attrs.get("email")
        otp = attrs.get("otp")

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError({"email": "User not found."})

        # Verify OTP
        otp_obj = PasswordResetOTP.objects.filter(
            user=user, otp=otp, is_used=False
        ).first()

        if not otp_obj:
            raise serializers.ValidationError({"otp": "Invalid verification code."})

        if not otp_obj.is_valid():
            raise serializers.ValidationError({"otp": "Verification code has expired."})

        attrs["otp_obj"] = otp_obj
        attrs["user"] = user
        return attrs


class GoogleAuthSerializer(serializers.Serializer):
    """
    Serializer for Google OAuth authentication.

    Validates Google ID token and returns user data.
    Uses GoogleOAuthService for token verification.
    """

    id_token = serializers.CharField(required=True, write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.google_service = GoogleOAuthService()

    def validate_id_token(self, value):
        """
        Verify Google ID token and extract user info.

        Args:
            value: Google ID token string

        Returns:
            Dictionary containing verified user information

        Raises:
            ValidationError: If token is invalid
        """
        return self.google_service.verify_token(value)

    def validate(self, attrs):
        """
        Store the verified Google user data for later use.
        """
        # The id_token field now contains the verified user data
        attrs['google_user_data'] = attrs['id_token']
        return attrs
