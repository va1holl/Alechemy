from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("scenarios/", views.scenario_list, name="scenario_list"),
    path("scenarios/<slug:slug>/favorite/", views.toggle_favorite_scenario, name="toggle_favorite"),
    path("scenarios/<slug:slug>/", views.scenario_detail, name="scenario_detail"),
    path("scenarios/<slug:slug>/create-event/", views.event_create_from_scenario, name="event_create_from_scenario"),

    path("events/", views.event_list, name="event_list"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),
    path(
        "events/recommendations-preview/",
        views.event_recommendations_preview,
        name="event_recommendations_preview",
    ),
]
