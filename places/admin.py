from django.contrib import admin
from .models import Place, Promotion

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "city", "is_active")
    list_filter = ("kind", "city", "is_active")
    search_fields = ("name", "city", "address")

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("title", "place", "valid_to", "is_active")
    list_filter = ("place", "valid_to", "is_active")
    search_fields = ("title", "description")
