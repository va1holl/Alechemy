from django.contrib import admin
from .models import Scenario, Event, Drink, Dish


@admin.register(Drink)
class DrinkAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    filter_horizontal = ("drinks",)


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    filter_horizontal = ("drinks",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("user", "scenario", "date", "people_count", "intensity")
    list_filter = ("scenario", "intensity", "date")
    search_fields = ("title", "scenario__name", "user__email")
