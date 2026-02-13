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
    
    # Нові функції: локація, фідбек, учасники
    path("events/<int:pk>/location/", views.event_location, name="event_location"),
    path("events/<int:pk>/feedback/", views.event_feedback, name="event_feedback"),
    path("events/<int:pk>/participants/", views.event_participants, name="event_participants"),
    path("events/<int:pk>/invite/", views.event_invite_friend, name="event_invite_friend"),
    path("events/<int:pk>/remove-participant/<int:participant_pk>/", views.event_remove_participant, name="event_remove_participant"),
    path("events/<int:pk>/toggle-admin/<int:participant_pk>/", views.event_toggle_admin, name="event_toggle_admin"),
    path("events/<int:pk>/invitation/<str:action>/", views.event_invitation_response, name="event_invitation_response"),
    path("events/<int:pk>/discussion/", views.event_discussion, name="event_discussion"),
    path("events/<int:pk>/finish/", views.event_finish, name="event_finish"),

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
    
    # AJAX API для пошуку подій
    path("api/events/search/", views.event_search_api, name="event_search_api"),
]
