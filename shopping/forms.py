from .models import StageChoices, IntensityChoices
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from events.models import Event, Scenario, Dish
from .models import StageChoices



class ShoppingCalcForm(forms.Form):
    intensity = forms.ChoiceField(
        choices=IntensityChoices.choices,
        required=False,
        label=_("Інтенсивність"),
        initial=IntensityChoices.MEDIUM,
        widget=forms.RadioSelect,
    )
    # Робимо обов'язковим у clean (інакше Ajax кричить "обов'язкове поле")
    scenario = forms.ModelChoiceField(
        queryset=Scenario.objects.all().order_by("name"),
        required=False,
        label=_("Сценарій"),
        # За замовчуванням показуємо сценарій.
        # Якщо обрано event, сховаємо поле в __init__.
    )

    event = forms.ModelChoiceField(
        queryset=Event.objects.none(),
        required=False,
        label=_("Подія"),
    )

    dishes = forms.ModelMultipleChoiceField(
        queryset=Dish.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 10}),
        label=_("Страви"),
        help_text=_("Показуються страви з інгредієнтами."),
    )

    stages = forms.MultipleChoiceField(
        choices=StageChoices.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label=_("Етапи"),
    )

    # теж не обов'язкові: якщо нема, підставимо значення за замовчуванням/значення з event
    people_count = forms.IntegerField(required=False, min_value=1, max_value=50, label=_("Людей"))
    duration_hours = forms.IntegerField(required=False, min_value=1, max_value=48, label=_("Тривалість, годин"))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user is not None and getattr(user, "is_authenticated", False):
            from events.models import EventParticipant
            from django.db.models import Q
            # Власні івенти + ті, де користувач є прийнятим учасником
            self.fields["event"].queryset = Event.objects.filter(
                Q(user=user) |
                Q(event_participants__participant=user, event_participants__status=EventParticipant.Status.ACCEPTED)
            ).distinct().order_by("-date", "-id")
        else:
            self.fields["event"].queryset = Event.objects.none()

        qs = Dish.objects.filter(dish_ingredients__isnull=False).distinct().order_by("name")

        # Якщо обрано event і в нього є dish (навіть без інгредієнтів) — додамо до списку,
        # щоб його можна було прибрати/замінити
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
            from events.models import EventParticipant
            from django.db.models import Q
            # Доступ до власних івентів або тих, де учасник
            ev = Event.objects.filter(
                Q(pk=ev_id) & (
                    Q(user=user) |
                    Q(event_participants__participant=user, event_participants__status=EventParticipant.Status.ACCEPTED)
                )
            ).first()
            dish_id = getattr(ev, "dish_id", None) if ev else None

        if dish_id:
            qs = Dish.objects.filter(Q(dish_ingredients__isnull=False) | Q(pk=dish_id)).distinct().order_by("name")

        self.fields["dishes"].queryset = qs

        # Якщо обрано event (initial або POST) — сценарій беремо з нього,
        # а поле сценарію ховаємо, щоб не було плутанини.
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


        # якщо є event — підставимо все з нього
        if event:
            # сценарій жорстко беремо з event, щоб не було розсинхрону/підміни
            cleaned["scenario"] = event.scenario

            if not cleaned.get("people_count"):
                cleaned["people_count"] = getattr(event, "people_count", 4) or 4

            if not cleaned.get("duration_hours"):
                cleaned["duration_hours"] = getattr(event, "duration_hours", 4) or 4

            if not cleaned.get("intensity"):
                cleaned["intensity"] = getattr(event, "intensity", IntensityChoices.MEDIUM)


        # значення за замовчуванням, якщо все одно порожньо
        if not cleaned.get("people_count"):
            cleaned["people_count"] = 4
        if not cleaned.get("duration_hours"):
            cleaned["duration_hours"] = 4
        if not cleaned.get("intensity"):
            cleaned["intensity"] = IntensityChoices.MEDIUM
        if not cleaned.get("stages"):
            cleaned["stages"] = ["prep", "during", "recovery"]

        # фінальна перевірка: потрібен хоча б сценарій (зазвичай прийде через event)
        if not cleaned.get("scenario"):
            raise forms.ValidationError(_("Обери подію (або сценарій), щоб порахувати список покупок."))

        return cleaned