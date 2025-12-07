from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

from accounts.models import Profile
from .forms import ProfileForm


class HomeView(TemplateView):
    template_name = "pages/home.html"


class ProfileView(LoginRequiredMixin, View):
    """
    /pages/me/ — редактирование профиля пользователя.
    Эти данные потом использует BAC в алко-дневнике.
    """

    def get(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(instance=profile)
        return render(
            request,
            "pages/profile.html",
            {
                "profile": profile,
                "form": form,
            },
        )

    def post(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("pages:me")

        return render(
            request,
            "pages/profile.html",
            {
                "profile": profile,
                "form": form,
            },
        )
