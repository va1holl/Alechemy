from django.urls import path
from . import views

app_name = "places"

urlpatterns = [
    path("map/", views.map_view, name="map"),
    path("places.json", views.places_json, name="places_json"),
    path("place/<int:pk>/", views.place_detail, name="place_detail"),
]
