from django.contrib import admin
from .models import Cocktail, CocktailIngredient

class CocktailIngredientInline(admin.TabularInline):
    model = CocktailIngredient
    extra = 1

@admin.register(Cocktail)
class CocktailAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CocktailIngredientInline]
    search_fields = ("name", "description")
    list_filter = ("is_active",)

@admin.register(CocktailIngredient)
class CocktailIngredientAdmin(admin.ModelAdmin):
    list_display = ("cocktail", "ingredient", "amount", "unit")
    search_fields = ("cocktail__name", "ingredient__name")
