from django.db import models
from django.conf import settings
from events.models import Event

class EventRating(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="rating")
    stars = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.event}: {self.stars}★, {self.points} pts"

class UserScore(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="score")
    points_total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user}: {self.points_total} pts"

class Achievement(models.Model):
    code = models.CharField(max_length=32, unique=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    points_reward = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "achievement")

    def __str__(self):
        return f"{self.user} - {self.achievement}"


class Challenge(models.Model):
    """
    Челендж — завдання, яке користувач може виконати за винагороду.
    Наприклад: "Створи 3 події цього тижня", "Спробуй 5 різних коктейлів".
    """
    class Difficulty(models.TextChoices):
        EASY = "easy", "Легко"
        MEDIUM = "medium", "Середнє"
        HARD = "hard", "Складно"

    code = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.EASY)
    points_reward = models.PositiveIntegerField(default=10)
    target_count = models.PositiveIntegerField(default=1, help_text="Скільки разів потрібно виконати дію")
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=10, default="🎯")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.icon} {self.title}"


class UserChallenge(models.Model):
    """
    Прогрес користувача у челенджі.
    """
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "В процесі"
        COMPLETED = "completed", "Виконано"
        CLAIMED = "claimed", "Нагороду отримано"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="challenges")
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="user_challenges")
    progress = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "challenge")

    def __str__(self):
        return f"{self.user} - {self.challenge.title}: {self.progress}/{self.challenge.target_count}"

    @property
    def progress_percent(self):
        if self.challenge.target_count == 0:
            return 100
        return min(100, int(self.progress / self.challenge.target_count * 100))

    @property
    def is_complete(self):
        return self.progress >= self.challenge.target_count