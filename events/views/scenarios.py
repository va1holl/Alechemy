"""
Scenario views - listing, detail, favorites.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from accounts.decorators import adult_required
from ..models import Scenario, Dish, Drink
from ..forms import ScenarioDrinkForm


@login_required
@adult_required
def scenario_list(request):
    """Список сценаріїв з фільтрацією за категорією."""
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
    """Додати/видалити сценарій з улюблених."""
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
    """Деталі сценарію з вибором напоїв, страв та розрахунками."""
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
            intensity_multiplier = {"low": 0.6, "medium": 1.0, "high": 1.5}.get(intensity, 1.0)
            
            # Розрахунок порцій для кожного напою
            total_items = len(selected_drinks) + len(selected_cocktails)
            if total_items > 0:
                for drink in selected_drinks:
                    if drink.strength == "strong":
                        portions_per_person_hour = 1.0
                        portion_ml = 40
                        portion_name = "шот (40мл)"
                    elif drink.strength == "non_alcoholic":
                        portions_per_person_hour = 2.0
                        portion_ml = 200
                        portion_name = "склянка (200мл)"
                    else:  # regular
                        portions_per_person_hour = 1.5
                        portion_ml = 150
                        portion_name = "бокал (150мл)"
                    
                    portions_per_person = int(
                        portions_per_person_hour * duration_hours * intensity_multiplier / total_items
                    )
                    portions_per_person = max(1, portions_per_person)
                    
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
                        "bottles": max(1, (total_ml + 749) // 750),
                    })
                
                for cocktail in selected_cocktails:
                    if cocktail.strength == "non_alcoholic":
                        portions_per_person_hour = 2.0
                        portion_ml = 250
                    elif cocktail.strength in ["strong", "very_strong"]:
                        portions_per_person_hour = 1.0
                        portion_ml = 120
                    else:
                        portions_per_person_hour = 1.5
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
