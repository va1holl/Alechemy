# pages/urls.py
from django.urls import path
from .views import HomeView, ProfileView

app_name = "pages"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("me/", ProfileView.as_view(), name="me"),
]
