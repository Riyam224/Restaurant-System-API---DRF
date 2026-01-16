from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from django.utils.html import format_html

User = get_user_model()


class CustomAdminSite(admin.AdminSite):
    """
    Custom admin site with enhanced dashboard statistics
    """

    def index(self, request, extra_context=None):
        """
        Override the default admin index view to add custom statistics
        """
        extra_context = extra_context or {}

        # Import models here to avoid circular imports
        try:
            from orders.models import Order
            from menu.models import Product
            from reviews.models import Review

            # Get statistics
            extra_context['orders_count'] = Order.objects.count()
            extra_context['products_count'] = Product.objects.count()
            extra_context['users_count'] = User.objects.filter(is_active=True).count()

            # Calculate total revenue from completed orders
            total_revenue = Order.objects.filter(
                status='COMPLETED',
                payment_status='PAID'
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0
            extra_context['total_revenue'] = total_revenue

            # Recent orders (last 5)
            extra_context['recent_orders'] = Order.objects.select_related('user').order_by('-created_at')[:5]

            # Order statistics by status
            extra_context['completed_orders'] = Order.objects.filter(status='COMPLETED').count()
            extra_context['pending_orders'] = Order.objects.filter(status='PENDING').count()

            # Product statistics
            extra_context['available_products'] = Product.objects.filter(is_available=True).count()

            # Review statistics
            extra_context['reviews_count'] = Review.objects.count()

        except Exception as e:
            # If models don't exist yet, pass empty values
            extra_context.update({
                'orders_count': 0,
                'products_count': 0,
                'users_count': 0,
                'total_revenue': 0,
                'recent_orders': [],
                'completed_orders': 0,
                'pending_orders': 0,
                'available_products': 0,
                'reviews_count': 0,
            })

        return super().index(request, extra_context)


# Create an instance of the custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')
