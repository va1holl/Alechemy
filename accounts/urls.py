# accounts/urls.py
from django.urls import path
from .views import (
    SignUpView, EmailLoginView, EmailLogoutView,
    MyPasswordChangeView, MyPasswordChangeDoneView,
    MyPasswordResetView, MyPasswordResetDoneView,
    MyPasswordResetConfirmView, MyPasswordResetCompleteView
)

app_name = "accounts"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", EmailLoginView.as_view(), name="login"),
    path("logout/", EmailLogoutView.as_view(), name="logout"),

    path("password_change/", MyPasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", MyPasswordChangeDoneView.as_view(), name="password_change_done"),

    path("password_reset/", MyPasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", MyPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", MyPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", MyPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
