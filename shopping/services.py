from collections import defaultdict
from decimal import Decimal

from events.models import DishIngredient
from .models import (
    IntensityChoices,
    ItemCategoryChoices,
    ScenarioSupplyTemplate,
    UnitChoices,
)


def _intensity_multiplier(intensity: str) -> Decimal:
    return {
        IntensityChoices.LOW: Decimal("0.85"),
        IntensityChoices.NORMAL: Decimal("1.00"),
        IntensityChoices.HIGH: Decimal("1.15"),
    }.get(intensity, Decimal("1.00"))


def _water_l_per_person_per_hour(intensity: str) -> Decimal:
    return {
        IntensityChoices.LOW: Decimal("0.25"),
        IntensityChoices.NORMAL: Decimal("0.33"),
        IntensityChoices.HIGH: Decimal("0.40"),
    }.get(intensity, Decimal("0.33"))


def _ice_kg_per_person_per_hour(intensity: str) -> Decimal:
    return {
        IntensityChoices.LOW: Decimal("0.08"),
        IntensityChoices.NORMAL: Decimal("0.10"),
        IntensityChoices.HIGH: Decimal("0.12"),
    }.get(intensity, Decimal("0.10"))


def _label_for_category(category: str) -> str:
    try:
        return ItemCategoryChoices(category).label
    except Exception:
        return str(category)


def _label_for_unit(unit: str) -> str:
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
    intensity: str,
    dishes=None,
):
    """
    Возвращает список dict'ов: [{name, category, category_label, unit, unit_label, qty}, ...]
    """
    if not stages:
        stages = []

    mult = _intensity_multiplier(intensity)

    rows = ScenarioSupplyTemplate.objects.filter(scenario=scenario, stage__in=stages)

    bucket = defaultdict(Decimal)  # (name, category, unit) -> qty

    for r in rows:
        qty = (r.qty_per_person_per_hour * Decimal(people_count) * Decimal(duration_hours)) * mult
        if qty <= 0:
            continue
        key = (r.name.strip(), r.category, r.unit)
        bucket[key] += qty

    # ингредиенты из выбранных блюд (если есть)
    if dishes:
        di_qs = DishIngredient.objects.filter(dish__in=dishes).select_related("ingredient", "dish")
        for di in di_qs:
            qty = di.qty_per_person * Decimal(people_count)
            if qty <= 0:
                continue
            name = di.ingredient.name.strip()
            category = ItemCategoryChoices.FOOD
            unit = di.unit  # значения совпадают с UnitChoices: pcs/g/kg/ml/l
            bucket[(name, category, unit)] += qty

    # базовые позиции
    water_qty = _water_l_per_person_per_hour(intensity) * Decimal(people_count) * Decimal(duration_hours)
    bucket[("Вода", ItemCategoryChoices.WATER, UnitChoices.L)] += water_qty

    ice_qty = _ice_kg_per_person_per_hour(intensity) * Decimal(people_count) * Decimal(duration_hours)
    bucket[("Лёд", ItemCategoryChoices.ICE, UnitChoices.KG)] += ice_qty

    items = []
    for (name, category, unit), qty in bucket.items():
        items.append(
            {
                "name": name,
                "category": category,
                "category_label": _label_for_category(category),
                "unit": unit,
                "unit_label": _label_for_unit(unit),
                "qty": qty.quantize(Decimal("0.001")),
            }
        )

    items.sort(key=lambda x: (x["category"], x["name"], x["unit"]))
    return items