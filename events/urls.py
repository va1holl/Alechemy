from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    # сценарии
    path("scenarios/", views.scenario_list, name="scenario_list"),
    path("scenarios/<slug:slug>/favorite/", views.toggle_favorite_scenario, name="toggle_favorite"),
    path("scenarios/<slug:slug>/", views.scenario_detail, name="scenario_detail"),
    path("scenarios/<slug:slug>/create-event/", views.event_create_from_scenario, name="event_create_from_scenario"),

    # события
    path("events/", views.event_list, name="event_list"),
    path("events/<int:pk>/", views.event_detail, name="event_detail"),
    path("events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),

    # алко-дневник
    path("diary/", views.diary_list, name="diary_list"),
    path("diary/add/", views.diary_add, name="diary_add"),
    path("events/<int:event_pk>/diary/add/", views.diary_add, name="diary_add_for_event"),
    path("diary/<int:pk>/", views.diary_detail, name="diary_detail"),

    # ajax-рекомендации
    path(
        "events/recommendations-preview/",
        views.event_recommendations_preview,
        name="event_recommendations_preview",
    ),
]
