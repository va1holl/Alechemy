from decimal import ROUND_HALF_UP, Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import render, get_object_or_404, redirect

from .models import Scenario, Event, Dish, Drink, AlcoholLog
from .forms import (
    ScenarioDrinkForm,
    EventCreateFromScenarioForm,
    EventUpdateForm,
    AlcoholLogForm,
)

import math
from django.http import JsonResponse
from django.views.decorators.http import require_POST

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


def build_recommendations_placeholder(
    user,
    scenario,
    drink,
    dish,
    people_count=None,
    duration_hours=None,
    intensity=None,
):
    """
    Простейший калькулятор под Event.

    Считает:
    - ориентировочный объём напитка на человека и всего,
    - сколько это бутылок по 0.75,
    - объём воды,
    - примерное количество порций еды,
    - очень грубую оценку BAC на одного (по профилю пользователя), если есть данные.

    Это НЕ рекомендация "столько выпей", а просто ориентировочные цифры.
    """
    profile = getattr(user, "profile", None)

    # --- входные параметры ---

    try:
        people = int(people_count) if people_count else 2
    except (TypeError, ValueError):
        people = 2

    try:
        hours = int(duration_hours) if duration_hours else 2
    except (TypeError, ValueError):
        hours = 2

    if people < 1:
        people = 1
    if hours < 1:
        hours = 1

    # intensity приходит строкой ("low"/"medium"/"high") или None
    intensity_code = intensity or Event.Intensity.MEDIUM
    if isinstance(intensity_code, Event.Intensity):
        intensity_code = intensity_code.value

    # коэффициент "агрессивности" по интенсивности
    if intensity_code == Event.Intensity.LOW:
        intensity_factor = 0.5
    elif intensity_code == Event.Intensity.HIGH:
        intensity_factor = 1.5
    else:
        intensity_factor = 1.0

    # --- расчёт алкоголя ---

    # базовый объём "порции" напитка в мл
    # для вина норм взять 150 мл, сейчас у тебя всё крутится вокруг вина
    base_serving_volume_ml = 150

    servings_per_person = max(1.0, hours * intensity_factor)
    per_person_alcohol_ml = int(servings_per_person * base_serving_volume_ml)
    total_alcohol_ml = per_person_alcohol_ml * people
    bottles_750_ml = max(1, math.ceil(total_alcohol_ml / 750))

    # --- вода ---

    # минимум 500 мл на человека, плюс по ~300 мл за каждый час
    per_person_water_ml = max(500, int(hours * 300))
    total_water_ml = per_person_water_ml * people
    water_bottles_1500_ml = max(1, math.ceil(total_water_ml / 1500))

    # --- еда ---

    if intensity_code == Event.Intensity.LOW:
        food_factor = 1.0
    elif intensity_code == Event.Intensity.HIGH:
        food_factor = 2.0
    else:
        food_factor = 1.5

    food_portions = max(1, math.ceil(people * food_factor))

    # --- базовый текст ---

    summary = (
        f"Оценка: на {people} человек при длительности {hours} ч "
        f"получается примерно {per_person_alcohol_ml} мл напитка на человека "
        f"(всего ~{total_alcohol_ml} мл, это около {bottles_750_ml} бутылок по 0.75 л). "
        f"Воды стоит заложить не меньше {per_person_water_ml} мл на человека "
        f"(всего ~{total_water_ml} мл, ≈{water_bottles_1500_ml} бутылок по 1.5 л) "
        f"и ориентироваться примерно на {food_portions} порций еды."
    )

    bac_promille = None

    if profile and drink and getattr(drink, "abv", None):
        dummy_log = AlcoholLog(
            user=user,
            drink=drink,
            volume_ml=per_person_alcohol_ml,
            abv=drink.abv,
        )
        bac_promille = dummy_log.calculate_bac()

        if bac_promille is not None:
            summary += (
                f" Для тебя это может дать около {bac_promille} ‰ в пике "
                f"(очень приблизительно, не использовать для решений про вождение и здоровье)."
            )
        else:
            summary += (
                " Для оценки BAC нужно корректно заполнить вес/пол в профиле."
            )
    elif profile:
        summary += (
            " Для расчёта BAC нужен напиток с указанной крепостью и заполненные вес/пол в профиле."
        )

    return {
        "summary": summary,
        "people": people,
        "hours": hours,
        "per_person_alcohol_ml": per_person_alcohol_ml,
        "total_alcohol_ml": total_alcohol_ml,
        "bottles_750_ml": bottles_750_ml,
        "per_person_water_ml": per_person_water_ml,
        "total_water_ml": total_water_ml,
        "water_bottles_1500_ml": water_bottles_1500_ml,
        "food_portions": food_portions,
        "bac_promille": bac_promille,
    }


def build_recovery_advice(user, drink, recommendations):
    """
    Текст: как отойти после такого объёма алкоголя.
    Используем оценочный BAC и стандартную скорость выведения.
    """
    if not recommendations:
        return None

    bac = recommendations.get("bac_promille")
    if not bac:
        # если не смогли посчитать BAC (нет профиля, веса и т.п.) – ничего умного не скажем
        return None

    if not isinstance(bac, Decimal):
        bac = Decimal(str(bac))

    # Очень приблизительная скорость выведения: 0.15 ‰ в час
    elimination_rate = Decimal("0.15")
    hours_to_zero = (bac / elimination_rate).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    per_person_water_ml = recommendations.get("per_person_water_ml") or 0
    try:
        per_person_water_ml = int(per_person_water_ml)
    except (TypeError, ValueError):
        per_person_water_ml = 0

    extra_water_ml = max(0, int(per_person_water_ml * 0.5))  # +50% к базовой воде

    text = (
        f"При таком объёме напитка ориентировочный пик для тебя — около {bac} ‰. "
        f"Организм в среднем выводит примерно 0.15 ‰ алкоголя в час, так что до почти полного "
        f"отрезвления может пройти около {hours_to_zero} ч. "
    )

    if extra_water_ml > 0:
        text += (
            f"После события стоит переключиться на воду: выпить ещё хотя бы {extra_water_ml} мл "
            f"поверх того, что планировалось во время вечера, и нормально поесть."
        )
    else:
        text += "После события стоит переключиться на воду и нормальную еду."

    text += (
        " Эта оценка очень приблизительная и не годится для решений про вождение, "
        "здоровье или дозировки лекарств."
    )

    return text


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
            event = form.save()
            return redirect("events:event_detail", pk=event.pk)
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


@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    scenario = event.scenario

    recommendations = build_recommendations_placeholder(
        user=request.user,
        scenario=scenario,
        drink=event.drink,
        dish=event.dish,
        people_count=event.people_count,
        duration_hours=event.duration_hours,
        intensity=event.intensity,
    )

    recovery_advice = build_recovery_advice(
        user=request.user,
        drink=event.drink,
        recommendations=recommendations,
    )

    return render(
        request,
        "events/event_detail.html",
        {
            "event": event,
            "scenario": scenario,
            "recommendations": recommendations,
            "recovery_advice": recovery_advice,
        },
    )


@require_POST
@login_required
def event_recommendations_preview(request):
    """
    AJAX-эндпоинт:
    принимает сценарий, напиток, блюдо, people_count, duration_hours, intensity,
    возвращает JSON с рекомендациями.
    """
    scenario_id = request.POST.get("scenario_id")
    drink_id = request.POST.get("drink_id")
    dish_id = request.POST.get("dish_id")

    people_count = request.POST.get("people_count")
    duration_hours = request.POST.get("duration_hours")
    intensity = request.POST.get("intensity")

    scenario = get_object_or_404(Scenario, id=scenario_id)
    drink = get_object_or_404(Drink, id=drink_id) if drink_id else None
    dish = get_object_or_404(Dish, id=dish_id) if dish_id else None

    rec = build_recommendations_placeholder(
        request.user,
        scenario,
        drink,
        dish,
        people_count=people_count,
        duration_hours=duration_hours,
        intensity=intensity,
    )
    return JsonResponse(rec)


@login_required
def diary_list(request):
    """
    Список записей алко-дневника текущего пользователя.
    """
    logs = (
        AlcoholLog.objects
        .filter(user=request.user)
        .select_related("event", "drink")
        .order_by("-taken_at", "-created_at")
    )
    return render(
        request,
        "events/diary_list.html",
        {"logs": logs},
    )

@login_required
def diary_detail(request, pk):
    log = get_object_or_404(AlcoholLog, pk=pk, user=request.user)
    return render(
        request,
        "events/diary_detail.html",
        {
            "log": log,
        },
    )


@login_required
def diary_add(request, event_pk=None):
    """
    Добавление записи в дневник.
    Если передан event_pk — пробуем привязать запись к событию.
    """
    event = None
    if event_pk is not None:
        event = get_object_or_404(Event, pk=event_pk, user=request.user)

    if request.method == "POST":
        form = AlcoholLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            if event and not log.event:
                log.event = event
            log.save()
            return redirect("events:diary_list")
    else:
        initial = {}
        if event is not None:
            initial["event"] = event
        form = AlcoholLogForm(initial=initial)

    return render(
        request,
        "events/diary_add.html",
        {"form": form, "event": event},
    )


def get_diary_stats_for_user(user):
    qs = AlcoholLog.objects.filter(user=user)

    if not qs.exists():
        return None

    last_log = qs.order_by("-taken_at").first()
    max_bac = qs.aggregate(Max("bac_estimate"))["bac_estimate__max"]

    return {
        "count": qs.count(),
        "max_bac": max_bac,
        "last_log": last_log,
    }