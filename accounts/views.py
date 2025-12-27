# accounts/views.py
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from .forms import SignUpForm, EmailAuthenticationForm
from .rate_limit import rate_limit


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("accounts:welcome")

    def form_valid(self, form):
        response = super().form_valid(form)
        # Если хочешь автологин после регистрации:
        # login(self.request, self.object)
        return response


@method_decorator(rate_limit('login', limit=5, period=60, block_time=300), name='post')
class EmailLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = "registration/login.html"
    redirect_authenticated_user = True

class EmailLogoutView(LogoutView):
    next_page = reverse_lazy("pages:home")

class MyPasswordChangeView(PasswordChangeView):
    template_name = "registration/password_change_form.html"
    success_url = reverse_lazy("accounts:password_change_done")

class MyPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "registration/password_change_done.html"

class MyPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.txt"
    subject_template_name = "registration/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")

    @method_decorator(rate_limit('password_reset', limit=3, period=300, block_time=900))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"

class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")

class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"
