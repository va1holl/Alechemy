from django import forms
from django.utils.translation import gettext_lazy as _

from .models import AlcoholLog, Dish, Drink, Event


class ScenarioDrinkForm(forms.Form):
    """Форма вибору напоїв (алкоголь та/або коктейлі) та параметрів події."""
    
    # Множинний вибір напоїв
    drinks = forms.ModelMultipleChoiceField(
        queryset=Drink.objects.none(),
        label=_("Напої"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    
    # Множинний вибір коктейлів
    cocktails = forms.ModelMultipleChoiceField(
        queryset=None,
        label=_("Коктейлі"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    
    # Множинний вибір страв
    dishes = forms.ModelMultipleChoiceField(
        queryset=Dish.objects.none(),
        label=_("Страви"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    # Параметри для розрахунку
    people_count = forms.IntegerField(
        label=_("Кількість людей"),
        initial=2,
        min_value=1,
        max_value=100,
        widget=forms.NumberInput(attrs={"class": "param-input", "min": "1", "max": "100"}),
    )
    
    duration_hours = forms.IntegerField(
        label=_("Тривалість (годин)"),
        initial=3,
        min_value=1,
        max_value=24,
        widget=forms.NumberInput(attrs={"class": "param-input", "min": "1", "max": "24"}),
    )
    
    intensity = forms.ChoiceField(
        label=_("Темп вечірки"),
        choices=[
            ("low", _("🐢 Спокійно")),
            ("medium", _("🎉 Нормально")),
            ("high", _("🔥 Жорстко")),
        ],
        initial="medium",
        widget=forms.RadioSelect,
    )

    difficulty = forms.ChoiceField(
        label=_("Складність страви"),
        required=False,
        widget=forms.RadioSelect,
        choices=[("", _("Будь-яка"))] + list(Dish.Difficulty.choices),
    )

    def __init__(self, *args, **kwargs):
        scenario = kwargs.pop("scenario", None)
        super().__init__(*args, **kwargs)
        
        # Зберігаємо сценарій та рекомендовані ID
        self.scenario = scenario
        
        # Всі напої, рекомендовані будуть позначені окремо
        all_drinks = Drink.objects.all().order_by("name")
        self.fields["drinks"].queryset = all_drinks
        
        if scenario is not None:
            self.recommended_drink_ids = set(scenario.drinks.values_list("id", flat=True))
        else:
            self.recommended_drink_ids = set()
        
        # Налаштування коктейлів
        from recipes.models import Cocktail
        self.fields["cocktails"].queryset = Cocktail.objects.filter(
            is_active=True
        ).order_by("category", "name")
        
        # Налаштування страв
        all_dishes = Dish.objects.all().order_by("name")
        self.fields["dishes"].queryset = all_dishes
        
        if scenario is not None:
            self.recommended_dish_ids = set(
                Dish.objects.filter(drinks__in=scenario.drinks.all())
                .distinct()
                .values_list("id", flat=True)
            )
        else:
            self.recommended_dish_ids = set()
    
    def clean(self):
        cleaned_data = super().clean()
        drinks = cleaned_data.get("drinks")
        cocktails = cleaned_data.get("cocktails")
        
        # Має бути вибрано хоча б щось одне
        if not drinks and not cocktails:
            # Не викидаємо помилку, просто нічого не буде розраховано
            pass
        
        return cleaned_data


class EventCreateFromScenarioForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "date", "people_count", "duration_hours", "notes"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input", "placeholder": "Назва заходу"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "people_count": forms.NumberInput(attrs={"class": "time-input", "min": "1"}),
            "duration_hours": forms.NumberInput(attrs={"class": "time-input", "min": "1"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-textarea", "placeholder": "Опишіть завдання..."}),
        }


class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "date",
            "people_count",
            "duration_hours",
            "intensity",
            "notes",
            "drink",
            "drinks",
            "dish",
            "dishes",
            "cocktails",
            "location_name",
            "location_address",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "intensity": forms.RadioSelect,
            "location_name": forms.TextInput(attrs={"placeholder": _("Назва місця, напр. Бар Шухляда")}),
            "location_address": forms.TextInput(attrs={"placeholder": _("Адреса, напр. вул. Хрещатик 1")}),
            "drinks": forms.CheckboxSelectMultiple,
            "dishes": forms.CheckboxSelectMultiple,
            "cocktails": forms.CheckboxSelectMultiple,
        }
        labels = {
            "location_name": _("Назва місця"),
            "location_address": _("Адреса"),
            "drinks": _("Напої"),
            "dishes": _("Страви"),
            "cocktails": _("Коктейлі"),
        }

    def __init__(self, *args, **kwargs):
        scenario = kwargs.pop("scenario", None)
        super().__init__(*args, **kwargs)

        if scenario is None and self.instance.pk:
            scenario = self.instance.scenario

        # Зберігаємо сценарій для використання в шаблоні
        self.scenario = scenario
        
        # Всі напої, але рекомендовані сценарію будуть першими
        all_drinks = Drink.objects.all().order_by("name")
        if scenario is not None:
            recommended_ids = set(scenario.drinks.values_list("id", flat=True))
            self.recommended_drink_ids = recommended_ids
        else:
            self.recommended_drink_ids = set()
        
        self.fields["drink"].queryset = all_drinks
        self.fields["drinks"].queryset = all_drinks

        # Коктейлі
        from recipes.models import Cocktail
        self.fields["cocktails"].queryset = Cocktail.objects.filter(is_active=True).order_by("category", "name")

        drink = None
        if self.is_bound:
            drink_id = self.data.get(self.add_prefix("drink"))
            if drink_id:
                try:
                    drink = Drink.objects.get(pk=drink_id)
                except Drink.DoesNotExist:
                    drink = None
        else:
            drink = self.instance.drink

        if drink is not None:
            self.fields["dish"].queryset = Dish.objects.filter(drinks=drink).order_by("name")
        else:
            self.fields["dish"].queryset = Dish.objects.all().order_by("name")


class AlcoholLogForm(forms.ModelForm):
    class Meta:
        model = AlcoholLog
        fields = ["event", "drink", "volume_ml", "taken_at", "abv", "note"]
        widgets = {
            "taken_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if "event" in self.fields:
            if user is not None and getattr(user, "is_authenticated", False):
                self.fields["event"].queryset = Event.objects.filter(user=user).order_by("-date", "-id")
            else:
                self.fields["event"].queryset = Event.objects.none()