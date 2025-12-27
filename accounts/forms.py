# accounts/forms.py
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.core.exceptions import ValidationError

User = get_user_model()


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Повторіть пароль",
        strip=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        # UI приймає лише email+паролі; username генеруємо з email.
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add hCaptcha field if enabled
        if getattr(settings, 'HCAPTCHA_ENABLED', False):
            from hcaptcha.fields import hCaptchaField
            self.fields['hcaptcha'] = hCaptchaField()
        
        # Проставляємо класи і плейсхолдери під верстку
        common_input = {
            "class": "w-full bg-transparent outline-none text-[18px] text-[#111]",
        }
        placeholders = {
            "email": "you@example.com",
            "password1": "Пароль",
            "password2": "Повторіть пароль",
        }

        for name, field in self.fields.items():
            if name == 'hcaptcha':
                continue  # Skip captcha field styling
            attrs = dict(common_input)
            if placeholders.get(name):
                attrs["placeholder"] = placeholders[name]
            field.widget.attrs.update(attrs)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise ValidationError("Вкажіть email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Користувач з таким email вже зареєстрований")
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if not p1 or not p2:
            raise ValidationError("Введіть пароль двічі")
        if p1 != p2:
            raise ValidationError("Паролі не збігаються")
        if len(p1) < 8:
            raise ValidationError("Пароль повинен бути не менше 8 символів")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        # username обязателен в AbstractUser; подставляем email
        user.username = self.cleaned_data.get("email") or user.username
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    """
    Авторизация по email: поле username ведёт себя как email.
    """
    username = UsernameField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "autofocus": True,
                "autocomplete": "email",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_input = {
            "class": "w-full bg-transparent outline-none text-[18px] text-[#111]",
        }
        if "username" in self.fields:
            self.fields["username"].widget.attrs.update({**common_input, "placeholder": "you@example.com"})
        if "password" in self.fields:
            self.fields["password"].widget.attrs.update({**common_input, "placeholder": "Пароль"})
