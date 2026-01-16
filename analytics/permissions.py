"""
Custom permissions for analytics endpoints.
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission class to allow only admin users to access analytics.
    """

    def has_permission(self, request, view):
        """
        Check if user is authenticated and is staff/admin.
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )

    message = "Only admin users can access analytics data."
