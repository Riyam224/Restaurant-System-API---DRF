from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # 🔐 Accounts APIs
    path("api/v1/", include("accounts.urls")),
    # 🍽 Menu APIs
    path("api/v1/", include("menu.urls")),
    # 🛒 Cart APIs
    path("api/v1/", include("cart.urls")),
    # 📦 Orders APIs
    path("api/v1/", include("orders.urls")),
]

# 📚 Swagger / OpenAPI
urlpatterns += [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
