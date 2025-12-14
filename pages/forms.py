from django import forms
from accounts.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "age",
            "sex",
            "height_cm",
            "weight_kg",
            "is_adult_confirmed",
            "gdpr_consent",
        ]
        widgets = {
            "age": forms.NumberInput(attrs={"min": 0}),
            "height_cm": forms.NumberInput(attrs={"min": 0}),
            "weight_kg": forms.NumberInput(attrs={"min": 0, "step": "0.1"}),
        }
        labels = {
            "age": "Возраст",
            "sex": "Пол",
            "height_cm": "Рост, см",
            "weight_kg": "Вес, кг",
            "is_adult_confirmed": "Мне есть 18 лет",
            "gdpr_consent": "Согласие на обработку данных",
        }
        help_texts = {
            "weight_kg": "Нужен для расчёта BAC в алко-дневнике.",
            "is_adult_confirmed": "Приложение рассчитано на пользователей 18+.",
            "gdpr_consent": "Нужно, чтобы хранить профиль и дневник.",
        }

    def clean(self):
        cleaned = super().clean()

        age = cleaned.get("age")
        is_adult_confirmed = cleaned.get("is_adult_confirmed")
        gdpr_consent = cleaned.get("gdpr_consent")

        if not gdpr_consent:
            self.add_error("gdpr_consent", "Нужно согласиться на обработку данных.")

        if not is_adult_confirmed:
            self.add_error("is_adult_confirmed", "Нужно подтвердить, что тебе 18+.")

        if age is None:
            self.add_error("age", "Укажи возраст (приложение 18+).")
        elif age < 18:
            self.add_error("age", "Доступ только для пользователей 18+.")

        return cleaned