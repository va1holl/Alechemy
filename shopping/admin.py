from django.contrib import admin

from .models import ScenarioSupplyTemplate, ShoppingItem, ShoppingList


@admin.register(ScenarioSupplyTemplate)
class ScenarioSupplyTemplateAdmin(admin.ModelAdmin):
    list_display = ("scenario", "stage", "name", "category", "qty_per_person_per_hour", "unit", "is_required")
    list_filter = ("stage", "category", "scenario")
    search_fields = ("name", "scenario__title")


class ShoppingItemInline(admin.TabularInline):
    model = ShoppingItem
    extra = 0


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "scenario", "event", "people_count", "duration_hours", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "user__username")
    inlines = [ShoppingItemInline]