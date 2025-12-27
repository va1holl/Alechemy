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
            "age": "Вік",
            "sex": "Стать",
            "height_cm": "Зріст, см",
            "weight_kg": "Вага, кг",
            "is_adult_confirmed": "Мені є 18 років",
            "gdpr_consent": "Згода на обробку даних",
        }
        help_texts = {
            "weight_kg": "Потрібно для розрахунку BAC в алко-щоденнику.",
            "is_adult_confirmed": "Додаток розрахований на користувачів 18+.",
            "gdpr_consent": "Потрібно для зберігання профілю і щоденника.",
        }

    def clean(self):
        cleaned = super().clean()

        age = cleaned.get("age")
        is_adult_confirmed = cleaned.get("is_adult_confirmed")
        gdpr_consent = cleaned.get("gdpr_consent")

        if not gdpr_consent:
            self.add_error("gdpr_consent", "Потрібно погодитись на обробку даних.")

        if not is_adult_confirmed:
            self.add_error("is_adult_confirmed", "Потрібно підтвердити, що тобі 18+.")

        if age is None:
            self.add_error("age", "Вкажи вік (додаток 18+).")
        elif age < 18:
            self.add_error("age", "Доступ тільки для користувачів 18+.")

        return cleaned