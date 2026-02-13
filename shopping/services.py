from collections import defaultdict
from decimal import Decimal

from events.models import DishIngredient
from recipes.models import CocktailIngredient

from .models import ItemCategoryChoices, ScenarioSupplyTemplate, UnitChoices


def _label_for_category(category: str) -> str:
    """Безпечно отримуємо людиночитабельний label категорії."""
    try:
        return ItemCategoryChoices(category).label
    except Exception:
        return str(category)


def _label_for_unit(unit: str) -> str:
    """Безпечно отримуємо людиночитабельний label одиниці."""
    try:
        return UnitChoices(unit).label
    except Exception:
        return str(unit)


def build_shopping_items(
    *,
    scenario,
    stages: list[str],
    people_count: int,
    duration_hours: int,
    dishes=None,
    cocktails=None,
):
    """
    Рахує підсумковий список покупок.

    ВАЖЛИВО: "інтенсивність" прибрана повністю. Вона ніде не потрібна і тільки
    створює несумісності (тепер всюди: low/medium/high).

    Повертає список dict'ів:
    [{name, category, category_label, unit, unit_label, qty}, ...]
    """

    stages = stages or []

    # шаблони за сценарієм/етапами
    rows = ScenarioSupplyTemplate.objects.filter(scenario=scenario, stage__in=stages)

    bucket: dict[tuple[str, str, str], Decimal] = defaultdict(Decimal)  # (name, category, unit) -> qty

    for r in rows:
        qty = r.qty_per_person_per_hour * Decimal(people_count) * Decimal(duration_hours)
        if qty <= 0:
            continue
        key = (r.name.strip(), r.category, r.unit)
        bucket[key] += qty

    # інгредієнти з обраних страв (якщо є)
    if dishes:
        di_qs = DishIngredient.objects.filter(dish__in=dishes).select_related("ingredient", "dish")
        for di in di_qs:
            qty = di.qty_per_person * Decimal(people_count)
            if qty <= 0:
                continue
            name = di.ingredient.name.strip()
            category = ItemCategoryChoices.FOOD
            unit = di.unit  # значення співпадають з UnitChoices: pcs/g/kg/ml/l
            bucket[(name, category, unit)] += qty

    # інгредієнти з обраних коктейлів (якщо є)
    if cocktails:
        ci_qs = CocktailIngredient.objects.filter(cocktail__in=cocktails).select_related("ingredient", "cocktail")
        for ci in ci_qs:
            qty = ci.amount * Decimal(people_count)
            if qty <= 0:
                continue
            name = ci.ingredient.name.strip()
            # Коктейльні інгредієнти - це ALCOHOL або FOOD залежно від типу інгредієнта
            category = ItemCategoryChoices.ALCOHOL if getattr(ci.ingredient, "is_alcoholic", False) else ItemCategoryChoices.FOOD
            unit = ci.unit
            bucket[(name, category, unit)] += qty

    # базові позиції (без "інтенсивності")
    # вода: 0.33 л на людину на годину
    water_qty = Decimal("0.33") * Decimal(people_count) * Decimal(duration_hours)
    bucket[("Вода", ItemCategoryChoices.WATER, UnitChoices.L)] += water_qty

    # лід: 0.10 кг на людину на годину
    ice_qty = Decimal("0.10") * Decimal(people_count) * Decimal(duration_hours)
    bucket[("Лід", ItemCategoryChoices.ICE, UnitChoices.KG)] += ice_qty

    items = []
    for (name, category, unit), qty in bucket.items():
        # Format quantity: whole number if integer, max 1 decimal otherwise
        qty_rounded = qty.quantize(Decimal("0.1"))
        if qty_rounded == qty_rounded.to_integral_value():
            qty_display = int(qty_rounded)
        else:
            qty_display = float(qty_rounded)
        items.append(
            {
                "name": name,
                "category": category,
                "category_label": _label_for_category(category),
                "unit": unit,
                "unit_label": _label_for_unit(unit),
                "qty": qty_display,
            }
        )

    items.sort(key=lambda x: (x["category"], x["name"], x["unit"]))
    return items