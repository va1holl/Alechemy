from django.urls import path
from . import views

app_name = "recipes"

urlpatterns = [
    path("", views.cocktail_list, name="cocktail_list"),
    path("search/", views.cocktail_search_by_ingredients, name="cocktail_search_by_ingredients"),
    path("ai-sommelier/", views.ai_sommelier, name="ai_sommelier"),
    path("ai-sommelier/api/", views.ai_sommelier_api, name="ai_sommelier_api"),
    path("<slug:slug>/", views.cocktail_detail, name="cocktail_detail"),
    path("<slug:slug>/review/", views.add_cocktail_review, name="add_cocktail_review"),
    path("<slug:slug>/add-to-event/", views.add_cocktail_to_event, name="add_cocktail_to_event"),
]
