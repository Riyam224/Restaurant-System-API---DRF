from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Root → API Docs
    path(
        "",
        RedirectView.as_view(url="/api/docs/", permanent=False),
        name="api-root",
    ),
    path("admin/", admin.site.urls),
    # APIs
    path("api/v1/", include("accounts.urls")),
    path("api/v1/", include("menu.urls")),
    path("api/v1/", include("cart.urls")),
    path("api/v1/", include("addresses.urls")),
    path("api/v1/", include("orders.urls")),
    path("api/v1/", include("reviews.urls")),
    path("api/v1/", include("coupons.urls")),
    # Docs and Schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
