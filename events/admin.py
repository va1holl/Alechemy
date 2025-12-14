from django.contrib import admin
from .models import (
    Scenario, Event, Drink, Dish,
    Ingredient, DishIngredient,
)


@admin.register(Drink)
class DrinkAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


class DishIngredientInline(admin.TabularInline):
    model = DishIngredient
    extra = 0


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    filter_horizontal = ("drinks",)
    inlines = [DishIngredientInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "default_unit")
    search_fields = ("name",)
    list_filter = ("category", "default_unit")


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    filter_horizontal = ("drinks",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # intensity не показываем вообще
    list_display = ("user", "scenario", "date", "people_count", "duration_hours")
    list_filter = ("scenario", "date")
    search_fields = ("title", "scenario__name", "user__email")