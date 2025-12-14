from django import forms
from django.db.models import Q

from events.models import Event, Scenario, Dish
from .models import StageChoices


class ShoppingCalcForm(forms.Form):
    # Делать обязательным будем в clean (иначе Ajax орёт “обязательное поле”)
    scenario = forms.ModelChoiceField(
        queryset=Scenario.objects.all().order_by("name"),
        required=False,
        label="Сценарий",
        # По умолчанию показываем сценарий.
        # Если выбран event, спрячем поле в __init__.
    )

    event = forms.ModelChoiceField(
        queryset=Event.objects.none(),
        required=False,
        label="Событие",
    )

    dishes = forms.ModelMultipleChoiceField(
        queryset=Dish.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 10}),
        label="Блюда",
        help_text="Показываются блюда с ингредиентами.",
    )

    stages = forms.MultipleChoiceField(
        choices=StageChoices.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Этапы",
    )

    # тоже не обязательные: если нет, подставим дефолты/значения из event
    people_count = forms.IntegerField(required=False, min_value=1, max_value=50, label="Людей")
    duration_hours = forms.IntegerField(required=False, min_value=1, max_value=48, label="Длительность, часов")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user is not None and getattr(user, "is_authenticated", False):
            self.fields["event"].queryset = Event.objects.filter(user=user).order_by("-date", "-id")
        else:
            self.fields["event"].queryset = Event.objects.none()

        qs = Dish.objects.filter(dish_ingredients__isnull=False).distinct().order_by("name")

        # Если выбран event и у него dish (даже без ингредиентов) — добавим в список,
        # чтобы его можно было убрать/заменить
        dish_id = None
        ev_id = None

        if self.is_bound:
            ev_id = self.data.get("event") or None
        else:
            initial_event = (self.initial or {}).get("event")
            if isinstance(initial_event, Event):
                ev_id = initial_event.id
            else:
                ev_id = initial_event

        if ev_id and user and getattr(user, "is_authenticated", False):
            ev = Event.objects.filter(pk=ev_id, user=user).first()
            dish_id = getattr(ev, "dish_id", None) if ev else None

        if dish_id:
            qs = Dish.objects.filter(Q(dish_ingredients__isnull=False) | Q(pk=dish_id)).distinct().order_by("name")

        self.fields["dishes"].queryset = qs

        # Если выбран event (initial или POST) — сценарий берём из него,
        # а поле сценария прячем, чтобы не было путаницы.
        event_value = None
        if self.is_bound:
            event_value = self.data.get("event") or None
        else:
            event_value = (self.initial or {}).get("event")

        if event_value:
            self.fields["scenario"].widget = forms.HiddenInput()

    def clean(self):
        cleaned = super().clean()

        event = cleaned.get("event")

        # если есть event — подставим всё из него
        if event:
            # сценарий жёстко берём из event, чтобы не было рассинхрона/подмены
            cleaned["scenario"] = event.scenario

            if not cleaned.get("people_count"):
                cleaned["people_count"] = getattr(event, "people_count", 4) or 4

            if not cleaned.get("duration_hours"):
                cleaned["duration_hours"] = getattr(event, "duration_hours", 4) or 4

        # дефолты, если всё равно пусто
        if not cleaned.get("people_count"):
            cleaned["people_count"] = 4
        if not cleaned.get("duration_hours"):
            cleaned["duration_hours"] = 4
        if not cleaned.get("stages"):
            cleaned["stages"] = ["prep", "during", "recovery"]

        # финальная проверка: нужен хотя бы сценарий (обычно придёт через event)
        if not cleaned.get("scenario"):
            raise forms.ValidationError("Выбери событие (или сценарий), чтобы посчитать список покупок.")

        return cleaned