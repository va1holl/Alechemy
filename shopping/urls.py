from django.urls import path
from . import views

app_name = "shopping"

urlpatterns = [
    path("preview/", views.preview, name="preview"),
    path("ajax/preview/", views.ajax_preview, name="ajax_preview"),
    path("create/", views.create_from_preview, name="create"),
    path("my/", views.my_lists, name="my_lists"),
    path("<int:pk>/", views.detail, name="detail"),
]