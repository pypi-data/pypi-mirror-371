"""Minimal URL configuration for testing require2fa package."""

from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", lambda _request: HttpResponse("OK")),  # Minimal root URL for testing
]
