from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """
    Кастомный пользователь: логинимся по email, он уникальный.
    """
    email = models.EmailField(_("email address"), unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email or self.username


class Profile(models.Model):
    class Sex(models.TextChoices):
        MALE = "m", "Мужской"
        FEMALE = "f", "Женский"
        OTHER = "other", "Другое / не указано"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    # по ТЗ: возраст, пол, вес, рост
    age = models.PositiveIntegerField(null=True, blank=True, help_text="Полных лет")
    sex = models.CharField(
        max_length=10,
        choices=Sex.choices,
        blank=True,
        help_text="Нужно для более точной оценки BAC",
    )
    height_cm = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Рост в см",
    )
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Вес в кг, нужен для BAC",
    )

    favorite_scenarios = models.ManyToManyField(
        "events.Scenario",
        related_name="favorite_for_profiles",
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"Профиль {self.user.email or self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
