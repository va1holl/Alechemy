from decimal import ROUND_HALF_UP, Decimal
import math
import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Max, Sum, Avg, Count
from django.db.models.functions import TruncDate, TruncHour, ExtractHour, ExtractWeekDay
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils import timezone

from accounts.decorators import adult_required
from .models import Scenario, Event, Dish, Drink, AlcoholLog, EventParticipant
from .forms import (
    ScenarioDrinkForm,
    EventCreateFromScenarioForm,
    EventUpdateForm,
    AlcoholLogForm,
)


@login_required
@adult_required
def scenario_list(request):
    # Prefetch drinks for display optimization
    scenarios = Scenario.objects.prefetch_related('drinks').order_by("name")
    profile = getattr(request.user, "profile", None)

    # Фільтрація за категорією
    category_filter = request.GET.get("category", "")
    if category_filter:
        scenarios = scenarios.filter(category=category_filter)

    favorite_ids = set()
    if profile is not None and hasattr(profile, "favorite_scenarios"):
        favorite_ids = set(profile.favorite_scenarios.values_list("id", flat=True))

    favorite_scenarios = scenarios.filter(id__in=favorite_ids)
    other_scenarios = scenarios.exclude(id__in=favorite_ids)

    # Категорії для фільтрів
    categories = Scenario.Category.choices

    return render(
        request,
        "events/scenario_list.html",
        {
            "scenarios": scenarios,
            "favorite_scenarios": favorite_scenarios,
            "other_scenarios": other_scenarios,
            "favorite_ids": favorite_ids,
            "categories": categories,
            "current_category": category_filter,
        },
    )


@login_required
@adult_required
@require_POST
def toggle_favorite_scenario(request, slug):
    scenario = get_object_or_404(Scenario, slug=slug)
    profile = request.user.profile

    if scenario in profile.favorite_scenarios.all():
        profile.favorite_scenarios.remove(scenario)
    else:
        profile.favorite_scenarios.add(scenario)

    return redirect("events:scenario_list")


@login_required
@adult_required
def scenario_detail(request, slug):
    scenario = get_object_or_404(Scenario, slug=slug)
    profile = getattr(request.user, "profile", None)

    selected_drinks = []
    selected_cocktails = []
    selected_dishes = []
    selected_difficulty = ""
    dishes = None
    people_count = 2
    duration_hours = 3
    intensity = "medium"
    drink_calculations = []

    if request.method == "POST":
        form = ScenarioDrinkForm(request.POST, scenario=scenario)
        if form.is_valid():
            selected_drinks = list(form.cleaned_data.get("drinks") or [])
            selected_cocktails = list(form.cleaned_data.get("cocktails") or [])
            selected_dishes = list(form.cleaned_data.get("dishes") or [])
            selected_difficulty = form.cleaned_data.get("difficulty") or ""
            people_count = form.cleaned_data.get("people_count") or 2
            duration_hours = form.cleaned_data.get("duration_hours") or 3
            intensity = form.cleaned_data.get("intensity") or "medium"

            # Множник для інтенсивності
            # low: 0.5x, medium: 1x, high: 1.5x
            intensity_multiplier = {"low": 0.6, "medium": 1.0, "high": 1.5}.get(intensity, 1.0)
            
            # Розрахунок порцій для кожного напою
            total_items = len(selected_drinks) + len(selected_cocktails)
            if total_items > 0:
                # Базові порції на людину на годину:
                # Міцний (40%): 1 шот/год, Звичайний (12-15%): 1-2 бокали/год, Безалкогольний: 2 склянки/год
                
                for drink in selected_drinks:
                    if drink.strength == "strong":
                        portions_per_person_hour = 1.0  # 1 шот на годину
                        portion_ml = 40
                        portion_name = "шот (40мл)"
                    elif drink.strength == "non_alcoholic":
                        portions_per_person_hour = 2.0  # 2 склянки на годину
                        portion_ml = 200
                        portion_name = "склянка (200мл)"
                    else:  # regular
                        portions_per_person_hour = 1.5  # 1.5 бокала на годину
                        portion_ml = 150
                        portion_name = "бокал (150мл)"
                    
                    # Порції на людину за весь час, з урахуванням інтенсивності
                    # Ділимо на кількість напоїв (рівномірний розподіл)
                    portions_per_person = int(
                        portions_per_person_hour * duration_hours * intensity_multiplier / total_items
                    )
                    portions_per_person = max(1, portions_per_person)  # Мінімум 1 порція
                    
                    total_portions = portions_per_person * people_count
                    total_ml = total_portions * portion_ml
                    
                    drink_calculations.append({
                        "name": drink.name,
                        "type": "drink",
                        "strength": drink.get_strength_display() if drink.strength else "Звичайний",
                        "abv": drink.abv or 0,
                        "portion_ml": portion_ml,
                        "portion_name": portion_name,
                        "portions_per_person": portions_per_person,
                        "total_portions": total_portions,
                        "total_ml": total_ml,
                        "bottles": max(1, (total_ml + 749) // 750),  # пляшка 750мл, округлення вгору
                    })
                
                for cocktail in selected_cocktails:
                    # Коктейлі - 1 коктейль на 30-60 хв залежно від міцності
                    if cocktail.strength == "non_alcoholic":
                        portions_per_person_hour = 2.0  # 2 мокт/год
                        portion_ml = 250
                    elif cocktail.strength in ["strong", "very_strong"]:
                        portions_per_person_hour = 1.0  # 1 коктейль/год
                        portion_ml = 120
                    else:  # medium, light
                        portions_per_person_hour = 1.5  # 1.5 коктейля/год
                        portion_ml = 180
                    
                    portions_per_person = int(
                        portions_per_person_hour * duration_hours * intensity_multiplier / total_items
                    )
                    portions_per_person = max(1, portions_per_person)
                    
                    total_portions = portions_per_person * people_count
                    total_ml = total_portions * portion_ml
                    
                    drink_calculations.append({
                        "name": cocktail.name,
                        "type": "cocktail",
                        "strength": cocktail.get_strength_display() if cocktail.strength else "Середній",
                        "abv": 0,
                        "portion_ml": portion_ml,
                        "portion_name": f"коктейль ({portion_ml}мл)",
                        "portions_per_person": portions_per_person,
                        "total_portions": total_portions,
                        "total_ml": total_ml,
                    })

            # Отримуємо страви
            if selected_drinks or selected_cocktails:
                if selected_drinks:
                    qs = Dish.objects.filter(drinks__in=selected_drinks).distinct()
                else:
                    qs = Dish.objects.all()
                
                if selected_difficulty:
                    qs = qs.filter(difficulty=selected_difficulty)
                dishes = qs.order_by("name")[:12]
    else:
        form = ScenarioDrinkForm(scenario=scenario)

    # Отримуємо всі напої для відображення
    all_drinks = Drink.objects.all().order_by("name")
    recommended_drink_ids = set(scenario.drinks.values_list("id", flat=True))
    
    # Отримуємо всі страви для відображення
    all_dishes = Dish.objects.all().order_by("name")
    # Рекомендовані страви - ті, що прив'язані до рекомендованих напоїв сценарію
    recommended_dish_ids = set(
        Dish.objects.filter(drinks__in=scenario.drinks.all())
        .distinct()
        .values_list("id", flat=True)
    )
    
    # Отримуємо коктейлі для відображення
    from recipes.models import Cocktail
    cocktails = Cocktail.objects.filter(is_active=True).order_by("category", "name")
    
    # Групуємо коктейлі за категоріями
    cocktail_categories = {}
    for c in cocktails:
        cat = c.get_category_display() if c.category else "Інше"
        if cat not in cocktail_categories:
            cocktail_categories[cat] = []
        cocktail_categories[cat].append(c)

    context = {
        "scenario": scenario,
        "profile": profile,
        "form": form,
        "all_drinks": all_drinks,
        "recommended_drink_ids": recommended_drink_ids,
        "all_dishes": all_dishes,
        "recommended_dish_ids": recommended_dish_ids,
        "selected_drinks": selected_drinks,
        "selected_cocktails": selected_cocktails,
        "selected_dishes": selected_dishes,
        "selected_difficulty": selected_difficulty,
        "dishes": dishes,
        "cocktails": cocktails,
        "cocktail_categories": cocktail_categories,
        "people_count": people_count,
        "duration_hours": duration_hours,
        "intensity": intensity,
        "drink_calculations": drink_calculations,
    }
    
    # AJAX request - return partial HTML
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "events/partials/scenario_calculations.html", context)
    
    return render(request, "events/scenario_detail.html", context)


@login_required
@adult_required
def event_list(request):
    from django.db.models import Q
    
    # Події, де користувач є власником АБО прийнятим учасником
    all_events = Event.objects.filter(
        Q(user=request.user) |
        Q(
            event_participants__participant=request.user,
            event_participants__status=EventParticipant.Status.ACCEPTED
        )
    ).select_related("scenario", "drink", "dish").distinct().order_by("-date", "-created_at")
    
    # Розділяємо активні події та архів (завершені)
    show_archive = request.GET.get('archive') == '1'
    
    if show_archive:
        events = all_events.filter(is_finished=True)
    else:
        events = all_events.filter(is_finished=False)
    
    # Кількість в архіві для бейджа
    archive_count = all_events.filter(is_finished=True).count()
    
    # ID власних подій для відображення бейджа "Учасник"
    own_event_ids = set(Event.objects.filter(user=request.user).values_list('id', flat=True))
    
    return render(request, "events/event_list.html", {
        "events": events,
        "own_event_ids": own_event_ids,
        "show_archive": show_archive,
        "archive_count": archive_count,
    })


def build_recommendations_placeholder(
    user,
    scenario,
    drink,
    dish,
    people_count=None,
    duration_hours=None,
):
    """
    Калькулятор рекомендацій для події.

    Розраховує:
    - орієнтовний об'єм напою на людину і загалом,
    - скільки це пляшок по 0.75л,
    - об'єм води,
    - приблизну кількість порцій їжі,
    - оцінку BAC на людину (за профілем користувача), якщо є дані.
    """
    profile = getattr(user, "profile", None)

    # --- вхідні параметри ---
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

    # --- розрахунок алкоголю ---
    base_serving_volume_ml = 150  # "порція" для вина/лонгдрінка
    servings_per_person = max(1.0, float(hours))  # 1 порція на годину
    per_person_alcohol_ml = int(servings_per_person * base_serving_volume_ml)
    total_alcohol_ml = per_person_alcohol_ml * people
    bottles_750_ml = max(1, math.ceil(total_alcohol_ml / 750))

    # --- вода ---
    per_person_water_ml = max(500, int(hours * 300))
    total_water_ml = per_person_water_ml * people
    water_bottles_1500_ml = max(1, math.ceil(total_water_ml / 1500))

    # --- їжа ---
    food_factor = 1.5
    food_portions = max(1, math.ceil(people * food_factor))

    summary = (
        f"📊 Розрахунок на {people} {'людину' if people == 1 else 'людей'} при тривалості {hours} год: "
        f"≈{per_person_alcohol_ml} мл напою на людину "
        f"(всього ~{total_alcohol_ml} мл, це близько {bottles_750_ml} пляшок по 0.75 л). "
        f"💧 Води потрібно мінімум {per_person_water_ml} мл на людину "
        f"(всього ~{total_water_ml} мл, ≈{water_bottles_1500_ml} пляшок по 1.5 л). "
        f"🍽️ Їжі орієнтовно на {food_portions} порцій."
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
                f" 🍺 Для вас це може дати близько {bac_promille} ‰ BAC "
                f"(орієнтовно, не використовувати для рішень про керування авто)."
            )
        else:
            summary += " ℹ️ Для оцінки BAC заповніть вагу та стать у профілі."
    elif profile:
        summary += " ℹ️ Для розрахунку BAC потрібен напій з вказаною міцністю та заповнені дані профілю."

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
    Поради щодо відновлення після вживання алкоголю.
    Використовуємо оцінковий BAC та стандартну швидкість виведення.
    """
    if not recommendations:
        return None

    bac = recommendations.get("bac_promille")
    if not bac:
        return None

    if not isinstance(bac, Decimal):
        bac = Decimal(str(bac))

    elimination_rate = Decimal("0.15")
    hours_to_zero = (bac / elimination_rate).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    per_person_water_ml = recommendations.get("per_person_water_ml") or 0
    try:
        per_person_water_ml = int(per_person_water_ml)
    except (TypeError, ValueError):
        per_person_water_ml = 0

    extra_water_ml = max(0, int(per_person_water_ml * 0.5))

    text = (
        f"🌙 **Стадія відновлення**\n\n"
        f"При такому об'ємі напою орієнтовний пік для вас — близько {bac} ‰. "
        f"Організм в середньому виводить приблизно 0.15 ‰ алкоголю на годину, тому до майже повного "
        f"протверезіння може пройти близько **{hours_to_zero} год**.\n\n"
    )

    if extra_water_ml > 0:
        text += (
            f"💧 **Рекомендації:**\n"
            f"• Випийте ще хоча б {extra_water_ml} мл води понад те, що планувалося під час вечора\n"
            f"• Нормально поїжте\n"
            f"• Відпочиньте та виспіться"
        )
    else:
        text += "💧 Після події варто переключитись на воду та нормальну їжу."

    text += (
        "\n\n⚠️ _Ця оцінка дуже орієнтовна і не підходить для рішень щодо керування авто, "
        "здоров'я або дозування ліків._"
    )

    return text


@login_required
@adult_required
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
        # Support both singular (from event_create form) and plural (from scenario_detail form)
        drink_ids = request.POST.getlist("drink_ids")
        drink_id = request.POST.get("drink_id") or (drink_ids[0] if drink_ids else None)
        dish_ids = request.POST.getlist("dish_ids")
        dish_id = request.POST.get("dish_id") or (dish_ids[0] if dish_ids else None)
        difficulty = request.POST.get("difficulty") or ""

        drink = get_object_or_404(Drink, id=drink_id) if drink_id else None
        dishes = [get_object_or_404(Dish, id=dish_id)] if dish_id else []

        if step == "select_dish":
            form = EventCreateFromScenarioForm()
            recommendations = build_recommendations_placeholder(
                request.user, scenario, drink, dishes[0] if dishes else None
            )
            return render(
                request,
                "events/event_create.html",
                {
                    "scenario": scenario,
                    "drink": drink,
                    "dish": dishes[0] if dishes else None,
                    "dishes": dishes,
                    "difficulty": difficulty,
                    "form": form,
                    "recommendations": recommendations,
                },
            )

        form = EventCreateFromScenarioForm(request.POST)
        if form.is_valid() and drink:
            event = form.save(commit=False)
            event.user = request.user
            event.scenario = scenario
            event.drink = drink
            # Assign first selected dish or None
            event.dish = dishes[0] if dishes else None
            # Set intensity from scenario or default
            event.intensity = getattr(scenario, 'intensity', 'medium') or 'medium'
            event.save()
            # TODO: If you want to support multiple dishes, add M2M logic here

            # Нараховуємо бали за створення події
            from gamification.services import award_points
            award_points(request.user, 'event_create')
            
            return redirect("events:event_list")
        else:
            # Debug: print form errors and drink to console
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Event creation failed: form.errors={form.errors}, drink={drink}, drink_id={drink_id}")

        recommendations = build_recommendations_placeholder(
            request.user,
            scenario,
            drink,
            dishes[0] if dishes else None,
            people_count=request.POST.get("people_count"),
            duration_hours=request.POST.get("duration_hours"),
        )
        return render(
            request,
            "events/event_create.html",
            {
                "scenario": scenario,
                "drink": drink,
                "dish": dishes[0] if dishes else None,
                "dishes": dishes,
                "difficulty": difficulty,
                "form": form,
                "recommendations": recommendations,
            },
        )

    return redirect("events:scenario_detail", slug=slug)


@login_required
@adult_required
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
    )

    # Рекомендовані страви на основі напоїв сценарію
    all_dishes = Dish.objects.all().order_by("name")
    recommended_dish_ids = set()
    if scenario:
        recommended_dish_ids = set(
            Dish.objects.filter(drinks__in=scenario.drinks.all())
            .distinct()
            .values_list("id", flat=True)
        )

    return render(
        request,
        "events/event_edit.html",
        {
            "event": event,
            "scenario": scenario,
            "form": form,
            "recommendations": recommendations,
            "all_dishes": all_dishes,
            "recommended_dish_ids": recommended_dish_ids,
        },
    )


@login_required
@adult_required
def event_delete(request, pk):
    """
    Удаление события. Только своего, без чужих приколов.
    """
    event = get_object_or_404(Event, pk=pk, user=request.user)

    if request.method == "POST":
        event.delete()
        return redirect("events:event_list")

    return redirect("events:event_edit", pk=pk)


@login_required
@adult_required
def event_detail(request, pk):
    # Безпечне отримання - 404 якщо немає доступу (запобігає ID enumeration)
    event = _get_accessible_event_or_404(pk, request.user)
    
    is_owner = event.user == request.user
    participant_record = EventParticipant.objects.filter(
        event=event, 
        participant=request.user
    ).first()
    is_participant = participant_record and participant_record.status == EventParticipant.Status.ACCEPTED
    
    scenario = event.scenario

    recommendations = build_recommendations_placeholder(
        user=request.user,
        scenario=scenario,
        drink=event.drink,
        dish=event.dish,
        people_count=event.people_count,
        duration_hours=event.duration_hours,
    )

    recovery_advice = build_recovery_advice(
        user=request.user,
        drink=event.drink,
        recommendations=recommendations,
    )
    
    # Отримуємо учасників
    participants = event.event_participants.select_related('participant__profile').all()
    accepted_participants = [p for p in participants if p.status == EventParticipant.Status.ACCEPTED]
    
    # Кількість повідомлень в обговоренні
    from .models import EventMessage
    messages_count = EventMessage.objects.filter(event=event).count()

    return render(
        request,
        "events/event_detail.html",
        {
            "event": event,
            "scenario": scenario,
            "recommendations": recommendations,
            "recovery_advice": recovery_advice,
            "is_owner": is_owner,
            "is_participant": is_participant,
            "participants": participants,
            "accepted_participants": accepted_participants,
            "messages_count": messages_count,
        },
    )


@require_POST
@login_required
@adult_required
def event_recommendations_preview(request):
    """
    AJAX-эндпоинт:
    принимает сценарий, напиток, блюдо, people_count, duration_hours,
    возвращает JSON с рекомендациями.
    """
    scenario_id = request.POST.get("scenario_id")
    drink_id = request.POST.get("drink_id")
    dish_id = request.POST.get("dish_id")

    people_count = request.POST.get("people_count")
    duration_hours = request.POST.get("duration_hours")

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
    )
    return JsonResponse(rec)


@login_required
@adult_required
def diary_list(request):
    """
    Список записей алко-дневника текущего пользователя з повною статистикою та графіками.
    """
    logs = (
        AlcoholLog.objects
        .filter(user=request.user)
        .select_related("event", "drink", "event__scenario")
        .order_by("-taken_at", "-created_at")
    )
    
    # === СТАТИСТИКА ===
    stats = {}
    
    if logs.exists():
        now = timezone.now()
        
        # Загальна статистика
        stats['total_logs'] = logs.count()
        stats['total_volume_ml'] = logs.aggregate(total=Sum('volume_ml'))['total'] or 0
        stats['avg_bac'] = logs.filter(bac_estimate__isnull=False).aggregate(avg=Avg('bac_estimate'))['avg']
        stats['max_bac'] = logs.filter(bac_estimate__isnull=False).aggregate(max=Max('bac_estimate'))['max']
        
        # Останній запис
        stats['last_log'] = logs.first()
        
        # Статистика за останній тиждень
        week_ago = now - timedelta(days=7)
        week_logs = logs.filter(taken_at__gte=week_ago)
        stats['week_logs'] = week_logs.count()
        stats['week_volume'] = week_logs.aggregate(total=Sum('volume_ml'))['total'] or 0
        
        # Статистика за останній місяць
        month_ago = now - timedelta(days=30)
        month_logs = logs.filter(taken_at__gte=month_ago)
        stats['month_logs'] = month_logs.count()
        stats['month_volume'] = month_logs.aggregate(total=Sum('volume_ml'))['total'] or 0
        
        # === ДАНІ ДЛЯ ГРАФІКІВ ===
        
        # 1. BAC по днях (останні 14 днів)
        two_weeks_ago = now - timedelta(days=14)
        bac_by_day = (
            logs.filter(taken_at__gte=two_weeks_ago, bac_estimate__isnull=False)
            .annotate(day=TruncDate('taken_at'))
            .values('day')
            .annotate(avg_bac=Avg('bac_estimate'), max_bac=Max('bac_estimate'))
            .order_by('day')
        )
        stats['bac_chart_labels'] = json.dumps([d['day'].strftime('%d.%m') for d in bac_by_day])
        stats['bac_chart_avg'] = json.dumps([float(d['avg_bac']) if d['avg_bac'] else 0 for d in bac_by_day])
        stats['bac_chart_max'] = json.dumps([float(d['max_bac']) if d['max_bac'] else 0 for d in bac_by_day])
        
        # 2. Об'єм споживання по днях (останні 14 днів)
        volume_by_day = (
            logs.filter(taken_at__gte=two_weeks_ago)
            .annotate(day=TruncDate('taken_at'))
            .values('day')
            .annotate(total_volume=Sum('volume_ml'))
            .order_by('day')
        )
        stats['volume_chart_labels'] = json.dumps([d['day'].strftime('%d.%m') for d in volume_by_day])
        stats['volume_chart_data'] = json.dumps([d['total_volume'] for d in volume_by_day])
        
        # 3. Розподіл за годинами (коли п'ють найчастіше)
        hourly_distribution = (
            logs
            .annotate(hour=ExtractHour('taken_at'))
            .values('hour')
            .annotate(count=Count('id'))
            .order_by('hour')
        )
        hours_data = {h['hour']: h['count'] for h in hourly_distribution}
        stats['hourly_labels'] = json.dumps([f"{h:02d}:00" for h in range(24)])
        stats['hourly_data'] = json.dumps([hours_data.get(h, 0) for h in range(24)])
        
        # 4. Розподіл за днями тижня
        weekday_distribution = (
            logs
            .annotate(weekday=ExtractWeekDay('taken_at'))
            .values('weekday')
            .annotate(count=Count('id'), total_volume=Sum('volume_ml'))
            .order_by('weekday')
        )
        weekday_names = ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
        weekday_data = {w['weekday']: w for w in weekday_distribution}
        stats['weekday_labels'] = json.dumps(weekday_names)
        stats['weekday_count'] = json.dumps([weekday_data.get(i, {}).get('count', 0) for i in range(1, 8)])
        stats['weekday_volume'] = json.dumps([weekday_data.get(i, {}).get('total_volume', 0) or 0 for i in range(1, 8)])
        
        # 5. Топ напоїв
        top_drinks = (
            logs.filter(drink__isnull=False)
            .values('drink__name')
            .annotate(count=Count('id'), total_volume=Sum('volume_ml'))
            .order_by('-count')[:5]
        )
        stats['top_drinks'] = list(top_drinks)
        stats['top_drinks_labels'] = json.dumps([d['drink__name'] for d in top_drinks])
        stats['top_drinks_data'] = json.dumps([d['count'] for d in top_drinks])
        
        # 6. Тренд BAC за місяць (тижневі середні)
        bac_trend = (
            logs.filter(taken_at__gte=month_ago, bac_estimate__isnull=False)
            .annotate(day=TruncDate('taken_at'))
            .values('day')
            .annotate(avg_bac=Avg('bac_estimate'))
            .order_by('day')
        )
        stats['bac_trend_labels'] = json.dumps([d['day'].strftime('%d.%m') for d in bac_trend])
        stats['bac_trend_data'] = json.dumps([float(d['avg_bac']) if d['avg_bac'] else 0 for d in bac_trend])
    
    return render(
        request,
        "events/diary_list.html",
        {"logs": logs, "stats": stats},
    )


@login_required
@adult_required
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
@adult_required
def diary_add(request, event_pk=None):
    """
    Додавання запису в щоденник.
    Якщо передано event_pk — прив'язуємо запис до цієї події (якщо є доступ).
    """
    event = None
    if event_pk is not None:
        event = get_object_or_404(Event, pk=event_pk)
        if not _can_access_event(event, request.user):
            from django.contrib import messages
            messages.error(request, "У вас немає доступу до цієї події.")
            return redirect("events:event_list")

    if request.method == "POST":
        form = AlcoholLogForm(request.POST, user=request.user)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user

            if event is not None:
                log.event = event
            else:
                if log.event is not None and log.event.user_id != request.user.id:
                    form.add_error("event", "Не можна обрати чужу подію.")
                    return render(
                        request,
                        "events/diary_add.html",
                        {"form": form, "event": event},
                    )

            log.save()
            return redirect("events:diary_list")
    else:
        initial = {}
        if event is not None:
            initial["event"] = event
        form = AlcoholLogForm(initial=initial, user=request.user)

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


# ===============================
# Нові функції: Локація, Фідбек, Учасники
# ===============================

def _get_accessible_event_or_404(pk, user):
    """
    Безпечне отримання події - повертає 404 якщо подія не існує АБО користувач не має доступу.
    Запобігає ID enumeration attack.
    """
    from django.db.models import Q
    from django.http import Http404
    
    # Отримуємо події, до яких користувач має доступ:
    # 1. Власник події
    # 2. Прийнятий учасник
    event = Event.objects.filter(
        Q(pk=pk) & (
            Q(user=user) |
            Q(event_participants__participant=user, event_participants__status=EventParticipant.Status.ACCEPTED)
        )
    ).distinct().first()
    
    if event is None:
        raise Http404("Подію не знайдено")
    
    return event


def _get_admin_event_or_404(pk, user):
    """
    Безпечне отримання події для адмінів - 404 якщо подія не існує АБО користувач не адмін.
    """
    from django.db.models import Q
    from django.http import Http404
    
    event = Event.objects.filter(
        Q(pk=pk) & (
            Q(user=user) |
            Q(event_participants__participant=user, 
              event_participants__status=EventParticipant.Status.ACCEPTED,
              event_participants__role=EventParticipant.Role.HEAD)
        )
    ).distinct().first()
    
    if event is None:
        raise Http404("Подію не знайдено")
    
    return event


def _can_access_event(event, user):
    """Перевіряє, чи може користувач дістатися до події (власник або прийнятий учасник)."""
    if event.user == user:
        return True
    return EventParticipant.objects.filter(
        event=event,
        participant=user,
        status=EventParticipant.Status.ACCEPTED
    ).exists()


def _is_event_admin(event, user):
    """Перевіряє, чи є користувач адміном події (власник або HEAD)."""
    if event.user == user:
        return True
    return EventParticipant.objects.filter(
        event=event,
        participant=user,
        status=EventParticipant.Status.ACCEPTED,
        role=EventParticipant.Role.HEAD
    ).exists()


def _get_user_role(event, user):
    """Отримує роль користувача у події."""
    if event.user == user:
        return "owner"
    participant = EventParticipant.objects.filter(
        event=event,
        participant=user,
        status=EventParticipant.Status.ACCEPTED
    ).first()
    if participant:
        return participant.role
    return None


@login_required
@adult_required
def event_location(request, pk):
    """Сторінка з картою місця проведення події."""
    event = _get_accessible_event_or_404(pk, request.user)
    return render(request, "events/event_location.html", {"event": event})


@login_required
@adult_required
def event_feedback(request, pk):
    """Фідбек після події - оцінка та відгук."""
    event = _get_accessible_event_or_404(pk, request.user)
    
    if request.method == "POST":
        from django.utils import timezone
        
        rating = request.POST.get("rating")
        feedback_text = request.POST.get("feedback", "").strip()
        
        if rating:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    event.user_rating = rating
            except ValueError:
                pass
        
        event.feedback = feedback_text
        event.feedback_submitted_at = timezone.now()
        event.is_finished = True
        event.save()
        
        # Нараховуємо бали за завершення та оцінку події
        from gamification.services import award_points
        award_points(request.user, 'event_complete')
        if rating:
            award_points(request.user, 'event_rate')
        
        return redirect("events:event_detail", pk=event.pk)
    
    # Отримати відгуки учасників
    participants = event.event_participants.select_related('participant__profile').filter(
        feedback_submitted_at__isnull=False
    )
    
    return render(request, "events/event_feedback.html", {
        "event": event,
        "participants": participants,
        "average_rating": event.get_average_rating(),
    })


@login_required
@adult_required
def event_participants(request, pk):
    """Список учасників події."""
    event = _get_accessible_event_or_404(pk, request.user)
    
    is_owner = event.user == request.user
    is_admin = _is_event_admin(event, request.user)
    
    participants = event.event_participants.select_related('participant__profile').all()
    
    # Отримати список друзів для запрошення (тільки для адмінів)
    friends = []
    if is_admin:
        profile = getattr(request.user, "profile", None)
        if profile:
            friends = profile.get_friends()
            # Виключити тих, хто вже запрошений
            invited_ids = set(participants.values_list('participant_id', flat=True))
            friends = [f for f in friends if f.user_id not in invited_ids]
    
    return render(request, "events/event_participants.html", {
        "event": event,
        "participants": participants,
        "friends": friends,
        "is_owner": is_owner,
        "is_admin": is_admin,
    })


@login_required
@adult_required
@require_POST
def event_invite_friend(request, pk):
    """Запросити друга на подію (тільки адміни)."""
    # Безпечне отримання - 404 якщо не адмін
    event = _get_admin_event_or_404(pk, request.user)
    
    friend_tag = request.POST.get("friend_tag", "").strip()
    friend_id = request.POST.get("friend_id")
    
    from accounts.models import Profile
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    friend_user = None
    
    # Пошук за тегом
    if friend_tag:
        # Підтримка формату @tag або просто tag
        tag = friend_tag.lstrip("@").lower()
        try:
            friend_profile = Profile.objects.select_related('user').get(unique_tag__iexact=tag)
            friend_user = friend_profile.user
        except Profile.DoesNotExist:
            messages.error(request, f"Користувача з тегом @{tag} не знайдено.")
            return redirect("events:event_participants", pk=pk)
    elif friend_id:
        try:
            friend_user = User.objects.get(pk=friend_id)
        except User.DoesNotExist:
            messages.error(request, "Користувача не знайдено.")
            return redirect("events:event_participants", pk=pk)
    
    if friend_user:
        if friend_user == request.user:
            messages.error(request, "Не можна запросити себе.")
        else:
            participant, created = EventParticipant.objects.get_or_create(
                event=event,
                participant=friend_user
            )
            if created:
                messages.success(request, f"Запрошення надіслано {friend_user.email}!")
                
                # Нараховуємо бали за запрошення друга
                from gamification.services import award_points
                award_points(request.user, 'event_invite')
                
                # Створюємо сповіщення про запрошення на подію
                from accounts.models import Notification
                from django.urls import reverse
                Notification.objects.create(
                    user=friend_user,
                    notification_type=Notification.NotificationType.EVENT_INVITE,
                    title=f"Запрошення на подію",
                    message=f"{request.user.email} запросив вас на подію «{event.title or event.scenario.name}»",
                    action_required=True,
                    action_url=reverse("events:event_participants", kwargs={"pk": event.pk}),
                    related_user=request.user,
                    related_event=event
                )
            else:
                messages.info(request, f"{friend_user.email} вже запрошений.")
    
    return redirect("events:event_participants", pk=pk)


@login_required
@adult_required
@require_POST
def event_remove_participant(request, pk, participant_pk):
    """Видалити учасника з події (тільки адміни, власника видалити не можна)."""
    from django.contrib import messages
    
    # Безпечне отримання - 404 якщо не адмін
    event = _get_admin_event_or_404(pk, request.user)
    
    participant = get_object_or_404(EventParticipant, pk=participant_pk, event=event)
    
    # Захист власника - його не можна видалити
    if participant.participant == event.user:
        messages.error(request, "Не можна видалити організатора події.")
        return redirect("events:event_participants", pk=pk)
    
    # Призначені адміни не можуть видаляти інших адмінів (тільки власник)
    is_owner = event.user == request.user
    if not is_owner and participant.role == EventParticipant.Role.HEAD:
        messages.error(request, "Тільки організатор може видаляти адміністраторів.")
        return redirect("events:event_participants", pk=pk)
    
    participant.delete()
    messages.success(request, "Учасника видалено.")
    
    return redirect("events:event_participants", pk=pk)


@login_required
@adult_required
@require_POST
def event_invitation_response(request, pk, action):
    """Відповідь на запрошення на подію (accept/decline/maybe)."""
    from django.utils import timezone
    from django.contrib import messages
    
    participant = get_object_or_404(
        EventParticipant, 
        event_id=pk, 
        participant=request.user
    )
    
    if action == "accept":
        participant.status = EventParticipant.Status.ACCEPTED
        messages.success(request, "Ви прийняли запрошення!")
        
        # Нараховуємо бали за прийняття запрошення
        from gamification.services import award_points
        award_points(request.user, 'event_accept_invite')
        
    elif action == "decline":
        participant.status = EventParticipant.Status.DECLINED
        messages.info(request, "Ви відхилили запрошення.")
    elif action == "maybe":
        participant.status = EventParticipant.Status.MAYBE
        messages.info(request, "Відповідь збережено.")
    
    participant.responded_at = timezone.now()
    participant.save()
    
    return redirect("events:event_list")


@login_required
@adult_required
def event_discussion(request, pk):
    """Обговорення події (чат учасників)."""
    from .models import EventMessage
    
    # Безпечне отримання - 404 якщо немає доступу
    event = _get_accessible_event_or_404(pk, request.user)
    
    is_owner = event.user == request.user
    
    # Отримуємо повідомлення
    event_messages = event.messages.select_related('user__profile').all()
    
    # Обробка нового повідомлення
    if request.method == "POST":
        text = request.POST.get("message", "").strip()
        if text:
            EventMessage.objects.create(
                event=event,
                user=request.user,
                text=text
            )
            return redirect("events:event_discussion", pk=pk)
    
    return render(request, "events/event_discussion.html", {
        "event": event,
        "messages_list": event_messages,
        "is_owner": is_owner,
    })


@login_required
@adult_required
@require_POST
def event_toggle_admin(request, pk, participant_pk):
    """Призначити/зняти адміна (тільки власник події)."""
    from django.contrib import messages
    from django.http import Http404
    
    # Безпечне отримання - 404 якщо не власник
    event = Event.objects.filter(pk=pk, user=request.user).first()
    if event is None:
        raise Http404("Подію не знайдено")
    
    participant = get_object_or_404(EventParticipant, pk=participant_pk, event=event)
    
    # Перемикаємо роль
    if participant.role == EventParticipant.Role.HEAD:
        participant.role = EventParticipant.Role.PARTICIPANT
        messages.success(request, f"{participant.participant.profile.get_display_name()} тепер звичайний учасник.")
    else:
        participant.role = EventParticipant.Role.HEAD
        messages.success(request, f"{participant.participant.profile.get_display_name()} тепер адміністратор!")
    
    participant.save()
    return redirect("events:event_participants", pk=pk)


@login_required
@adult_required
@require_POST
def event_finish(request, pk):
    """Завершити подію та нарахувати бали всім учасникам."""
    from django.contrib import messages
    from django.utils import timezone
    from django.http import Http404
    from gamification.services import award_points
    
    # Безпечне отримання - 404 якщо не власник
    event = Event.objects.filter(pk=pk, user=request.user).first()
    if event is None:
        raise Http404("Подію не знайдено")
    
    if event.is_finished:
        messages.info(request, "Ця подія вже завершена.")
        return redirect("events:event_detail", pk=pk)
    
    # Позначаємо подію як завершену
    event.is_finished = True
    event.save(update_fields=["is_finished"])
    
    # Нараховуємо бали організатору за завершення події
    award_points(event.user, 'event_complete')
    
    # Нараховуємо бали всім прийнятим учасникам
    accepted_participants = event.event_participants.filter(
        status=EventParticipant.Status.ACCEPTED
    ).select_related('participant')
    
    for p in accepted_participants:
        # Адміни отримують більше балів
        if p.role == EventParticipant.Role.HEAD:
            award_points(p.participant, 'event_admin_complete')
        else:
            award_points(p.participant, 'event_participate')
    
    participant_count = accepted_participants.count()
    messages.success(
        request, 
        f"Подію завершено! Бали нараховано вам та {participant_count} учасникам."
    )
    
    return redirect("events:event_detail", pk=pk)