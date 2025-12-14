from django import forms

from .models import AlcoholLog, Dish, Drink, Event


class ScenarioDrinkForm(forms.Form):
    drink = forms.ModelChoiceField(
        queryset=Drink.objects.none(),
        label="Напиток",
        widget=forms.RadioSelect,
        empty_label=None,
    )

    difficulty = forms.ChoiceField(
        label="Сложность блюда",
        required=False,
        widget=forms.RadioSelect,
        choices=[("", "Любая")] + list(Dish.Difficulty.choices),
    )

    def __init__(self, *args, **kwargs):
        scenario = kwargs.pop("scenario", None)
        super().__init__(*args, **kwargs)
        if scenario is not None:
            self.fields["drink"].queryset = scenario.drinks.all().order_by("name")


class EventCreateFromScenarioForm(forms.ModelForm):
    class Meta:
        model = Event
        # intensity убрано
        fields = ["title", "date", "people_count", "duration_hours", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = Event
        # intensity убрано
        fields = [
            "title",
            "date",
            "people_count",
            "duration_hours",
            "notes",
            "drink",
            "dish",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        scenario = kwargs.pop("scenario", None)
        super().__init__(*args, **kwargs)

        if scenario is None and self.instance.pk:
            scenario = self.instance.scenario

        if scenario is not None:
            self.fields["drink"].queryset = scenario.drinks.all().order_by("name")
        else:
            self.fields["drink"].queryset = Drink.objects.all().order_by("name")

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