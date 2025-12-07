from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

from accounts.models import Profile
from events.views import get_diary_stats_for_user
from .forms import ProfileForm


class HomeView(TemplateView):
    template_name = "pages/home.html"


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(instance=profile)
        diary_stats = get_diary_stats_for_user(request.user)

        return render(
            request,
            "pages/profile.html",
            {
                "profile": profile,
                "form": form,
                "diary_stats": diary_stats,
            },
        )

    def post(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("pages:me")

        diary_stats = get_diary_stats_for_user(request.user)

        return render(
            request,
            "pages/profile.html",
            {
                "profile": profile,
                "form": form,
                "diary_stats": diary_stats,
            },
        )