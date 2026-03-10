# accounts/views.py
import hashlib
import logging
import secrets

import requests
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, \
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from .forms import SignUpForm, EmailAuthenticationForm
from .rate_limit import rate_limit

logger = logging.getLogger('accounts')


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("pages:personal_data")

    def form_valid(self, form):
        response = super().form_valid(form)
        # Зберігаємо підтвердження з форми реєстрації в профіль
        from accounts.models import Profile
        profile, _ = Profile.objects.get_or_create(user=self.object)
        profile.is_adult_confirmed = True
        profile.gdpr_consent = True
        profile.save(update_fields=['is_adult_confirmed', 'gdpr_consent'])
        # Автологін після реєстрації
        login(self.request, self.object, backend='accounts.backends.EmailBackend')
        # Email-привітання
        from accounts.emails import send_welcome_email
        send_welcome_email(self.object)
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
    html_email_template_name = "registration/password_reset_email.html"
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


# =============================================================================
# Google OAuth2
# =============================================================================

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def google_login(request):
    """Перенаправлення користувача на Google для авторизації."""
    # Генеруємо state для захисту від CSRF
    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state

    redirect_uri = request.build_absolute_uri(reverse('accounts:google_callback'))

    params = {
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'online',
        'state': state,
        'prompt': 'select_account',
    }
    url = GOOGLE_AUTH_URL + '?' + '&'.join(f'{k}={requests.utils.quote(str(v))}' for k, v in params.items())
    return redirect(url)


def google_callback(request):
    """Callback від Google після авторизації."""
    error = request.GET.get('error')
    if error:
        logger.warning(f"Google OAuth error: {error}")
        return redirect('accounts:login')

    code = request.GET.get('code')
    state = request.GET.get('state')

    # Перевіряємо state для захисту від CSRF
    expected_state = request.session.pop('google_oauth_state', None)
    if not state or not expected_state or state != expected_state:
        logger.warning("Google OAuth: invalid state parameter")
        return redirect('accounts:login')

    if not code:
        return redirect('accounts:login')

    redirect_uri = request.build_absolute_uri(reverse('accounts:google_callback'))

    # Обмін коду на токен
    token_data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }

    try:
        token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data, timeout=10)
        token_response.raise_for_status()
        tokens = token_response.json()
    except requests.RequestException:
        logger.exception("Google OAuth: token exchange failed")
        return redirect('accounts:login')

    access_token = tokens.get('access_token')
    if not access_token:
        logger.warning("Google OAuth: no access_token in response")
        return redirect('accounts:login')

    # Отримуємо інформацію про користувача
    try:
        userinfo_response = requests.get(
            GOOGLE_USERINFO_URL,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
    except requests.RequestException:
        logger.exception("Google OAuth: userinfo fetch failed")
        return redirect('accounts:login')

    email = userinfo.get('email')
    if not email or not userinfo.get('email_verified'):
        logger.warning("Google OAuth: email not verified")
        return redirect('accounts:login')

    name = userinfo.get('name', '')

    # Аутентифікуємо/створюємо користувача через бекенд
    user = authenticate(request, google_email=email, google_name=name)
    if user is not None:
        login(request, user, backend='accounts.backends.GoogleOAuth2Backend')
        logger.info(f"Google OAuth login: {email}")
        return redirect(settings.LOGIN_REDIRECT_URL)

    logger.warning(f"Google OAuth: authenticate returned None for {email}")
    return redirect('accounts:login')
