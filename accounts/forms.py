# accounts/forms.py
import random
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.core.exceptions import ValidationError

User = get_user_model()


class SimpleCaptchaMixin:
    """Міксін для простої математичної капчі."""
    
    def setup_captcha(self):
        """Налаштовує поля капчі."""
        # Генеруємо два числа для прикладу
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        
        # Визначаємо операцію (+ або -)
        if random.choice([True, False]):
            operation = '+'
            answer = num1 + num2
        else:
            # Для віднімання робимо так, щоб результат був додатнім
            if num1 < num2:
                num1, num2 = num2, num1
            operation = '-'
            answer = num1 - num2
        
        self.captcha_question = f"{num1} {operation} {num2} = ?"
        self.captcha_answer = answer
        
        # Додаємо поля
        self.fields['captcha_answer'] = forms.IntegerField(
            label=f"Скільки буде {num1} {operation} {num2}?",
            widget=forms.NumberInput(attrs={
                'class': 'w-full bg-transparent outline-none text-[18px] text-[#111]',
                'placeholder': 'Введіть відповідь',
                'autocomplete': 'off',
            }),
            required=True,
        )
        self.fields['captcha_hash'] = forms.CharField(
            widget=forms.HiddenInput(),
            initial=self._make_hash(answer),
        )
    
    def _make_hash(self, answer):
        """Створює простий хеш для перевірки відповіді."""
        import hashlib
        secret = getattr(settings, 'SECRET_KEY', 'fallback')[:16]
        return hashlib.sha256(f"{answer}{secret}".encode()).hexdigest()[:16]
    
    def clean_captcha_answer(self):
        """Перевіряє відповідь капчі."""
        answer = self.cleaned_data.get('captcha_answer')
        expected_hash = self.data.get('captcha_hash', '')
        
        if answer is None:
            raise ValidationError("Введіть відповідь на математичний приклад")
        
        if self._make_hash(answer) != expected_hash:
            raise ValidationError("Неправильна відповідь. Спробуйте ще раз.")
        
        return answer


class SignUpForm(SimpleCaptchaMixin, forms.ModelForm):
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
            if name in ('captcha_answer', 'captcha_hash'):
                continue  # Капча вже має свої стилі
            attrs = dict(common_input)
            if placeholders.get(name):
                attrs["placeholder"] = placeholders[name]
            field.widget.attrs.update(attrs)
        
        # Додаємо просту капчу
        self.setup_captcha()

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise ValidationError("Вкажіть email")
        # Case-insensitive перевірка (test@x.com == Test@X.com)
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Користувач з таким email вже зареєстрований")
        return email.lower()  # Зберігаємо в нижньому регістрі

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
