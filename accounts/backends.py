from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Login email and pass.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get("email") or username
        if email is None or password is None:
            return None
        try:
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None


class GoogleOAuth2Backend(ModelBackend):
    """
    Backend для авторизації через Google OAuth2.
    Аутентифікує користувача за email із Google-профілю.
    """
    def authenticate(self, request, google_email=None, google_name=None, **kwargs):
        if google_email is None:
            return None

        try:
            user = UserModel.objects.get(email__iexact=google_email)
        except UserModel.DoesNotExist:
            # Створюємо нового користувача
            username = google_email.split("@")[0]
            # Гарантуємо унікальність username
            base_username = username
            counter = 1
            while UserModel.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = UserModel.objects.create_user(
                username=username,
                email=google_email,
                password=None,  # Google-юзери не мають пароля
            )
            user.is_verified = True
            if google_name:
                parts = google_name.split(" ", 1)
                user.first_name = parts[0]
                if len(parts) > 1:
                    user.last_name = parts[1]
            user.save()

            # Встановлюємо підтвердження 18+ та GDPR для Google-юзерів
            from accounts.models import Profile
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.is_adult_confirmed = True
            profile.gdpr_consent = True
            profile.save(update_fields=['is_adult_confirmed', 'gdpr_consent'])

        if self.user_can_authenticate(user):
            return user
        return None
