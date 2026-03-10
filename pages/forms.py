from django import forms
from datetime import date
from accounts.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "birth_date",
            "sex",
            "height_cm",
            "weight_kg",
            "is_adult_confirmed",
            "gdpr_consent",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "height_cm": forms.NumberInput(attrs={"min": 0}),
            "weight_kg": forms.NumberInput(attrs={"min": 0, "step": "0.1"}),
        }
        labels = {
            "birth_date": "Дата народження",
            "sex": "Стать",
            "height_cm": "Зріст, см",
            "weight_kg": "Вага, кг",
            "is_adult_confirmed": "Мені є 18 років",
            "gdpr_consent": "Згода на обробку даних",
        }

    def clean(self):
        cleaned = super().clean()

        birth_date_val = cleaned.get("birth_date")
        is_adult_confirmed = cleaned.get("is_adult_confirmed")
        gdpr_consent = cleaned.get("gdpr_consent")

        if not gdpr_consent:
            self.add_error("gdpr_consent", "Потрібно погодитись на обробку даних.")

        if not is_adult_confirmed:
            self.add_error("is_adult_confirmed", "Потрібно підтвердити, що тобі 18+.")

        if birth_date_val is None:
            self.add_error("birth_date", "Вкажи дату народження (додаток 18+).")
        else:
            today = date.today()
            age = today.year - birth_date_val.year - (
                (today.month, today.day) < (birth_date_val.month, birth_date_val.day)
            )
            if age < 18:
                self.add_error("birth_date", "Доступ тільки для користувачів 18+.")

        return cleaned