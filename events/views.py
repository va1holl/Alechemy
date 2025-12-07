from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .models import Scenario, Event, Dish, Drink
from .forms import ScenarioDrinkForm, EventCreateFromScenarioForm, EventUpdateForm



@login_required
def scenario_list(request):
    scenarios = Scenario.objects.all().order_by("name")
    profile = getattr(request.user, "profile", None)

    favorite_ids = set()
    if profile is not None and hasattr(profile, "favorite_scenarios"):
        favorite_ids = set(profile.favorite_scenarios.values_list("id", flat=True))

    favorite_scenarios = scenarios.filter(id__in=favorite_ids)
    other_scenarios = scenarios.exclude(id__in=favorite_ids)

    return render(
        request,
        "events/scenario_list.html",
        {
            "scenarios": scenarios,
            "favorite_scenarios": favorite_scenarios,
            "other_scenarios": other_scenarios,
            "favorite_ids": favorite_ids,
        },
    )


@login_required
def toggle_favorite_scenario(request, slug):
    scenario = get_object_or_404(Scenario, slug=slug)
    profile = request.user.profile

    if scenario in profile.favorite_scenarios.all():
        profile.favorite_scenarios.remove(scenario)
    else:
        profile.favorite_scenarios.add(scenario)

    return redirect("events:scenario_list")


@login_required
def scenario_detail(request, slug):
    scenario = get_object_or_404(Scenario, slug=slug)
    profile = getattr(request.user, "profile", None)

    selected_drink = None
    selected_difficulty = ""
    dishes = None

    if request.method == "POST":
        form = ScenarioDrinkForm(request.POST, scenario=scenario)
        if form.is_valid():
            selected_drink = form.cleaned_data["drink"]
            selected_difficulty = form.cleaned_data.get("difficulty") or ""

            qs = Dish.objects.filter(drinks=selected_drink)
            if selected_difficulty:
                qs = qs.filter(difficulty=selected_difficulty)

            dishes = qs.order_by("name")
    else:
        form = ScenarioDrinkForm(scenario=scenario)

    return render(
        request,
        "events/scenario_detail.html",
        {
            "scenario": scenario,
            "profile": profile,
            "form": form,
            "selected_drink": selected_drink,
            "selected_difficulty": selected_difficulty,
            "dishes": dishes,
        },
    )


@login_required
def event_list(request):
    events = (
        Event.objects.filter(user=request.user)
        .select_related("scenario", "drink", "dish")
        .order_by("-date", "-created_at")
    )
    return render(request, "events/event_list.html", {"events": events})


def build_recommendations_placeholder(user, scenario, drink, dish, people_count=None, duration_hours=None, intensity=None):
    """
    Заглушка под будущий калькулятор алкоголя/еды.
    Здесь ты потом вставишь свою математику по граммовке, BAC и т.д.
    Сейчас это просто текст, чтобы флоу работал.
    """
    profile = getattr(user, "profile", None)
    parts = []

    if people_count:
        parts.append(f"Гостей: {people_count}")
    if duration_hours:
        parts.append(f"Длительность: {duration_hours} ч")
    if intensity:
        parts.append(f"Интенсивность: {intensity}")

    base = "Параметры события будут использованы для расчёта количества напитков и блюд."
    if parts:
        base += " " + ", ".join(parts) + "."

    if profile:
        base += " С учётом данных профиля расчёт можно будет сделать точнее."

    return {"summary": base}

@login_required
def event_create_from_scenario(request, slug):
    """
    Шаг 2:
    - сюда прилетаем из scenario_detail с drink_id + dish_id;
    - показываем форму параметров события;
    - после сабмита создаём Event и кидаем в 'мои события'.
    """
    scenario = get_object_or_404(Scenario, slug=slug)

    if request.method == "POST":
        step = request.POST.get("step", "select_dish")
        drink_id = request.POST.get("drink_id")
        dish_id = request.POST.get("dish_id")
        difficulty = request.POST.get("difficulty") or ""

        drink = get_object_or_404(Drink, id=drink_id) if drink_id else None
        dish = get_object_or_404(Dish, id=dish_id) if dish_id else None

        if step == "select_dish":
            # только что выбрали блюдо -> показываем форму параметров
            form = EventCreateFromScenarioForm()
            recommendations = build_recommendations_placeholder(
                request.user, scenario, drink, dish
            )
            return render(
                request,
                "events/event_create.html",
                {
                    "scenario": scenario,
                    "drink": drink,
                    "dish": dish,
                    "difficulty": difficulty,
                    "form": form,
                    "recommendations": recommendations,
                },
            )

        # step == "create_event" -> сохраняем
        form = EventCreateFromScenarioForm(request.POST)
        if form.is_valid() and drink and dish:
            event = form.save(commit=False)
            event.user = request.user
            event.scenario = scenario
            event.drink = drink
            event.dish = dish

            # сюда потом можно писать summary/цифры по расчёту
            # event.notes = "Автоматически рассчитанные рекомендации..."

            event.save()
            return redirect("events:event_list")

        recommendations = build_recommendations_placeholder(
            request.user, scenario, drink, dish,
            people_count=request.POST.get("people_count"),
            duration_hours=request.POST.get("duration_hours"),
            intensity=request.POST.get("intensity"),
        )
        return render(
            request,
            "events/event_create.html",
            {
                "scenario": scenario,
                "drink": drink,
                "dish": dish,
                "difficulty": difficulty,
                "form": form,
                "recommendations": recommendations,
            },
        )

    # прямой GET сюда не нужен — отправляем обратно к сценарию
    return redirect("events:scenario_detail", slug=slug)


@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    scenario = event.scenario

    if request.method == "POST":
        form = EventUpdateForm(request.POST, instance=event, scenario=scenario)
        if form.is_valid():
            form.save()
            return redirect("events:event_list")
    else:
        form = EventUpdateForm(instance=event, scenario=scenario)

    recommendations = build_recommendations_placeholder(
        request.user,
        scenario,
        form.instance.drink,
        form.instance.dish,
        people_count=form.instance.people_count,
        duration_hours=form.instance.duration_hours,
        intensity=form.instance.intensity,
    )

    return render(
        request,
        "events/event_edit.html",
        {
            "event": event,
            "scenario": scenario,
            "form": form,
            "recommendations": recommendations,
        },
    )

@login_required
def event_delete(request, pk):
    """
    Удаление события. Только своего, без чужих приколов.
    """
    event = get_object_or_404(Event, pk=pk, user=request.user)

    if request.method == "POST":
        event.delete()
        return redirect("events:event_list")

    # если вдруг зайдут GET-ом – просто редиректим
    return redirect("events:event_edit", pk=pk)