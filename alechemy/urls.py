"""
URL configuration for alechemy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django_otp.admin import OTPAdminSite

# Enable 2FA for admin panel
admin.site.__class__ = OTPAdminSite

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls", namespace="pages")),  # / ведёт на pages:home
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("events/", include("events.urls", namespace="events")),
    path("shopping/", include("shopping.urls")),
    path("places/", include("places.urls", namespace="places")),
    path("recipes/", include("recipes.urls", namespace="recipes")),
    path("social/", include("social.urls", namespace="social")),
    path("gamification/", include("gamification.urls", namespace="gamification")),
    path("stats/", include("stats.urls", namespace="stats")),
    path("health/", include("health.urls")),
    
    # REST API endpoints
    path("api/v1/auth/", include("accounts.api_urls", namespace="accounts_api")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
