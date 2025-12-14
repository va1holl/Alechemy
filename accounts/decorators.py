from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from accounts.models import Profile


def adult_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)

        if not profile.gdpr_consent:
            messages.error(request, "Нужно дать согласие на обработку данных (в профиле).")
            return redirect("pages:me")

        if not profile.is_adult_confirmed:
            messages.error(request, "Нужно подтвердить, что тебе 18+ (в профиле).")
            return redirect("pages:me")

        if profile.age is None:
            messages.error(request, "Укажи возраст в профиле (приложение 18+).")
            return redirect("pages:me")

        if profile.age < 18:
            messages.error(request, "Доступ только для пользователей 18+.")
            return redirect("pages:home")

        return view_func(request, *args, **kwargs)

    return _wrapped