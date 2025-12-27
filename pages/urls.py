# pages/urls.py
from django.urls import path
from .views import (
    HomeView, ProfileView, 
    notifications_view, notification_action, calculator_view,
    plan_choice_view, payment_form_view, payment_success_view,
    personal_data_view, dashboard_view, delete_account_view,
    privacy_policy_view, settings_view, set_language_view,
)

app_name = "pages"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("me/", ProfileView.as_view(), name="me"),
    path("me/personal-data/", personal_data_view, name="personal_data"),
    path("me/delete/", delete_account_view, name="delete_account"),
    path("notifications/", notifications_view, name="notifications"),
    path("notifications/<int:notification_id>/<str:action>/", notification_action, name="notification_action"),
    path("calculator/", calculator_view, name="calculator"),
    
    # Premium
    path("premium/", plan_choice_view, name="plan_choice"),
    path("premium/payment/", payment_form_view, name="payment_form"),
    path("premium/success/", payment_success_view, name="payment_success"),
    
    # Legal
    path("privacy-policy/", privacy_policy_view, name="privacy_policy"),
    
    # Settings
    path("settings/", settings_view, name="settings"),
    path("set-language/", set_language_view, name="set_language"),
]
