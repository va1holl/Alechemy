# pages/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(TemplateView):
    template_name = "pages/home.html"

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "pages/profile.html"
