# accounts/forms.py
from django import forms
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
        label="Повторите пароль",
        strip=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name")
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "username": forms.TextInput(attrs={"autocomplete": "username"}),
            "first_name": forms.TextInput(),
            "last_name": forms.TextInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise ValidationError("Укажите email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже зарегистрирован")
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if not p1 or not p2:
            raise ValidationError("Введите пароль дважды")
        if p1 != p2:
            raise ValidationError("Пароли не совпадают")
        if len(p1) < 8:
            raise ValidationError("Пароль должен быть не короче 8 символов")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
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
