from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from apps.accounts.api.v1.views import LoginView, RefreshView, LogoutView

from .views import health

schema_view = get_schema_view(
    openapi.Info(
        title="Account API",
        default_version="v1",
        description="This is a Test API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="moahamdshakiba09@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("token/create/", LoginView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", RefreshView.as_view(), name="token_refresh"),
    path("token/logout/", LogoutView.as_view(), name="token-logout"),
    path("accounts/", include("apps.accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
