from django import forms
from accounts.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["age", "sex", "height_cm", "weight_kg"]
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
        }
        help_texts = {
            "weight_kg": "Нужен для расчёта BAC в алко-дневнике.",
        }
