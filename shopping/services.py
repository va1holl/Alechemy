from collections import defaultdict
from decimal import Decimal

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
    # базовая вода, чтобы потом не делать вид, что люди фотосинтезируют
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


def build_shopping_items(
    *,
    scenario,
    stages: list[str],
    people_count: int,
    duration_hours: int,
    intensity: str,
):
    """
    Возвращает список dict'ов: [{name, category, unit, qty}, ...]
    """
    if not stages:
        stages = []  # ок, просто будет вода+лёд (и ничего из шаблонов)

    mult = _intensity_multiplier(intensity)

    rows = ScenarioSupplyTemplate.objects.filter(scenario=scenario, stage__in=stages)

    bucket = defaultdict(Decimal)  # key -> qty

    for r in rows:
        qty = (r.qty_per_person_per_hour * Decimal(people_count) * Decimal(duration_hours)) * mult
        if qty <= 0:
            continue
        key = (r.name.strip(), r.category, r.unit)
        bucket[key] += qty

    # Обязательные вещи по ТЗ: вода и лёд (даже если в шаблонах забыли)
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
                "unit": unit,
                "qty": qty.quantize(Decimal("0.001")),
            }
        )

    items.sort(key=lambda x: (x["category"], x["name"], x["unit"]))
    return items