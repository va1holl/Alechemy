from django.urls import path
from . import views

app_name = "social"

urlpatterns = [
    path("friends/", views.friends_list, name="friends_list"),
    path("friends/search/", views.search_users, name="search_users"),
    path("friends/send/<int:user_id>/", views.send_friend_request, name="send_friend_request"),
    path("friends/accept/<int:req_id>/", views.accept_friend_request, name="accept_friend_request"),
    path("friends/reject/<int:req_id>/", views.reject_friend_request, name="reject_friend_request"),
    path("leaderboard/", views.friends_leaderboard, name="friends_leaderboard"),
    path("user/<str:tag>/", views.user_profile_by_tag, name="user_profile_by_tag"),
]
