from django.urls import include, path

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("api/v1/", include("apps.accounts.api.v1.urls")),
]
