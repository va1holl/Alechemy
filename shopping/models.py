from decimal import Decimal

from django.conf import settings
from django.db import models


class StageChoices(models.TextChoices):
    PREP = "prep", "Подготовка"
    DURING = "during", "Во время"
    RECOVERY = "recovery", "Восстановление"


class IntensityChoices(models.TextChoices):
    LOW = "low", "Низкая"
    NORMAL = "normal", "Средняя"
    HIGH = "high", "Высокая"


class ItemCategoryChoices(models.TextChoices):
    ALCOHOL = "alcohol", "Алкоголь"
    FOOD = "food", "Еда"
    WATER = "water", "Вода"
    ICE = "ice", "Лёд"
    OTHER = "other", "Другое"


class UnitChoices(models.TextChoices):
    PCS = "pcs", "шт"
    ML = "ml", "мл"
    L = "l", "л"
    G = "g", "г"
    KG = "kg", "кг"


class ScenarioSupplyTemplate(models.Model):
    """
    Шаблон закупки: под конкретный сценарий и этап.
    Количество задаётся как "на 1 человека в 1 час".
    """
    scenario = models.ForeignKey(
        "events.Scenario",
        on_delete=models.CASCADE,
        related_name="supply_templates",
    )
    stage = models.CharField(max_length=16, choices=StageChoices.choices)

    name = models.CharField(max_length=120)
    category = models.CharField(
        max_length=16, choices=ItemCategoryChoices.choices, default=ItemCategoryChoices.OTHER
    )
    unit = models.CharField(max_length=8, choices=UnitChoices.choices, default=UnitChoices.PCS)

    qty_per_person_per_hour = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal("0.0"))
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ["scenario_id", "stage", "category", "name"]
        unique_together = ("scenario", "stage", "name", "unit", "category")

    def __str__(self):
        return f"{self.scenario} [{self.stage}] {self.name}"


class ShoppingList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shopping_lists")
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shopping_lists",
    )
    scenario = models.ForeignKey(
        "events.Scenario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shopping_lists",
    )

    people_count = models.PositiveIntegerField(default=4)
    duration_hours = models.PositiveIntegerField(default=4)
    intensity = models.CharField(max_length=16, choices=IntensityChoices.choices, default=IntensityChoices.NORMAL)

    # выбранные этапы (prep/during/recovery)
    stages = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    dishes = models.ManyToManyField("events.Dish", blank=True, related_name="shopping_lists")

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"ShoppingList #{self.id} ({self.user})"


class ShoppingItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name="items")

    name = models.CharField(max_length=120)
    category = models.CharField(
        max_length=16, choices=ItemCategoryChoices.choices, default=ItemCategoryChoices.OTHER
    )
    unit = models.CharField(max_length=8, choices=UnitChoices.choices, default=UnitChoices.PCS)
    qty = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.0"))

    is_auto = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "name", "unit", "id"]

    def __str__(self):
        return f"{self.name} {self.qty} {self.unit}"