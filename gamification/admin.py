from django.contrib import admin
from .models import EventRating, UserScore, Achievement, UserAchievement, Challenge, UserChallenge

@admin.register(EventRating)
class EventRatingAdmin(admin.ModelAdmin):
    list_display = ("event", "stars", "points")
    search_fields = ("event__title",)

@admin.register(UserScore)
class UserScoreAdmin(admin.ModelAdmin):
    list_display = ("user", "points_total")
    search_fields = ("user__username",)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "points_reward")
    search_fields = ("code", "title")

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ("user", "achievement", "earned_at")
    search_fields = ("user__username", "achievement__title")


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "difficulty", "points_reward", "target_count", "is_active")
    list_filter = ("difficulty", "is_active")
    search_fields = ("code", "title")


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    list_display = ("user", "challenge", "progress", "status", "started_at")
    list_filter = ("status",)
    search_fields = ("user__username", "challenge__title")
