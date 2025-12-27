from django.urls import path
from . import views

app_name = "gamification"

urlpatterns = [
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("my-achievements/", views.my_achievements, name="my_achievements"),
    path("challenges/", views.challenges_list, name="challenges"),
    path("challenges/<int:challenge_id>/claim/", views.claim_challenge_reward, name="claim_challenge"),
    
    # Mini-games
    path("games/cocktail-quiz/", views.cocktail_quiz, name="cocktail_quiz"),
    path("games/cocktail-quiz/question/", views.cocktail_quiz_question, name="cocktail_quiz_question"),
    path("games/cocktail-quiz/answer/", views.cocktail_quiz_answer, name="cocktail_quiz_answer"),
]
