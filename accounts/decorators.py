from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from accounts.models import Profile


def adult_required(view_func):
    """
    Decorator that ensures user is authenticated, has GDPR consent,
    and is confirmed 18+ before accessing the view.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # First check authentication
        if not request.user.is_authenticated:
            messages.error(request, "Потрібно увійти в акаунт.")
            return redirect("accounts:login")
        
        profile, _ = Profile.objects.get_or_create(user=request.user)

        if not profile.gdpr_consent:
            messages.error(request, "Нужно дать согласие на обработку данных (в профиле).")
            return redirect("pages:me")

        if not profile.is_adult_confirmed:
            messages.error(request, "Нужно подтвердить, что тебе 18+ (в профиле).")
            return redirect("pages:me")

        if profile.birth_date is None:
            messages.error(request, "Вкажи дату народження в профілі (додаток 18+).")
            return redirect("pages:personal_data")

        if profile.age < 18:
            messages.error(request, "Доступ тільки для користувачів 18+.")
            return redirect("pages:home")

        return view_func(request, *args, **kwargs)

    return _wrapped


def premium_required(view_func):
    """
    Decorator that ensures user is authenticated and has premium subscription.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        # First check authentication
        if not request.user.is_authenticated:
            messages.error(request, "Потрібно увійти в акаунт.")
            return redirect("accounts:login")
        
        profile, _ = Profile.objects.get_or_create(user=request.user)

        if not profile.is_premium:
            messages.warning(request, "Ця функція доступна тільки Premium-користувачам.")
            return redirect("pages:plan_choice")

        return view_func(request, *args, **kwargs)

    return _wrapped