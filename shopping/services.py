from collections import defaultdict
from decimal import Decimal

from events.models import DishIngredient

from .models import ItemCategoryChoices, ScenarioSupplyTemplate, UnitChoices


def _label_for_category(category: str) -> str:
    """Безопасно получаем человекочитаемый label категории."""
    try:
        return ItemCategoryChoices(category).label
    except Exception:
        return str(category)


def _label_for_unit(unit: str) -> str:
    """Безопасно получаем человекочитаемый label единицы."""
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
):
    """
    Считает итоговый список покупок.

    ВАЖНО: "интенсивность" убрана полностью. Она нигде не нужна и только плодит
    несовместимости (events: low/medium/high vs shopping: low/normal/high).

    Возвращает список dict'ов:
    [{name, category, category_label, unit, unit_label, qty}, ...]
    """

    stages = stages or []

    # шаблоны по сценарию/этапам
    rows = ScenarioSupplyTemplate.objects.filter(scenario=scenario, stage__in=stages)

    bucket: dict[tuple[str, str, str], Decimal] = defaultdict(Decimal)  # (name, category, unit) -> qty

    for r in rows:
        qty = r.qty_per_person_per_hour * Decimal(people_count) * Decimal(duration_hours)
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

    # базовые позиции (без "интенсивности")
    # вода: 0.33 л на человека в час
    water_qty = Decimal("0.33") * Decimal(people_count) * Decimal(duration_hours)
    bucket[("Вода", ItemCategoryChoices.WATER, UnitChoices.L)] += water_qty

    # лёд: 0.10 кг на человека в час
    ice_qty = Decimal("0.10") * Decimal(people_count) * Decimal(duration_hours)
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