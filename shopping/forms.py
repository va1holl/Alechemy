from django import forms

from events.models import Event, Scenario
from .models import IntensityChoices, StageChoices


class ShoppingCalcForm(forms.Form):
    scenario = forms.ModelChoiceField(queryset=Scenario.objects.all(), required=True)
    event = forms.ModelChoiceField(queryset=Event.objects.none(), required=False)

    stages = forms.MultipleChoiceField(
        choices=StageChoices.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    people_count = forms.IntegerField(min_value=1, max_value=50, initial=4)
    duration_hours = forms.IntegerField(min_value=1, max_value=48, initial=4)
    intensity = forms.ChoiceField(choices=IntensityChoices.choices, initial=IntensityChoices.NORMAL)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user is not None and getattr(user, "is_authenticated", False):
            self.fields["event"].queryset = Event.objects.filter(user=user).order_by("-date", "-id")
        else:
            self.fields["event"].queryset = Event.objects.none()
