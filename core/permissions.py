from rest_framework.permissions import BasePermission, SAFE_METHODS

try:
    from rest_framework_api_key.permissions import HasAPIKey
except ImportError:  # pragma: no cover - optional dependency
    class HasAPIKey:  # type: ignore
        """
        Fallback when rest_framework_api_key is not installed.
        Denies unless replaced by the real class.
        """

        def has_permission(self, request, view):
            return False


def _is_authenticated(request) -> bool:
    """
    Shared authenticated check to avoid repeating the same logic.
    """
    return bool(request.user and request.user.is_authenticated)


class ReadWithAPIKeyWriteWithJWT(BasePermission):
    """
    - SAFE methods (GET, HEAD, OPTIONS): allow with API Key OR authenticated user
    - Write methods: JWT authenticated users only
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            if HasAPIKey().has_permission(request, view):
                return True
            return _is_authenticated(request)

        return _is_authenticated(request)


class IsAdminUserJWT(BasePermission):
    """
    Allows access only to admin users using JWT.
    """

    def has_permission(self, request, view):
        return _is_authenticated(request) and request.user.is_staff


class IsOwner(BasePermission):
    """
    Object-level permission: user can only access their own object.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAuthenticatedJWT(BasePermission):
    """
    JWT authenticated users only.
    """

    def has_permission(self, request, view):
        return _is_authenticated(request)
