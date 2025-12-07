from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """
    Кастомный пользователь: логинимся по email, он уникальный.
    username остаётся (требование AbstractUser), но можем не светить его в формах.
    """
    email = models.EmailField(_("email address"), unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email or self.username


class Profile(models.Model):
    """
    Профиль пользователя: базовые физические параметры,
    которые дальше будем использовать в расчётах из ТЗ.
    """

    class Gender(models.TextChoices):
        MALE = "male", _("Мужчина")
        FEMALE = "female", _("Женщина")
        OTHER = "other", _("Другое")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    age = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Возраст"),
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        verbose_name=_("Пол"),
    )
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Вес (кг)"),
    )
    height_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Рост (см)"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Профиль {self.user.email or self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Гарантируем, что у каждого пользователя есть Profile.
    При создании юзера – создаём профиль.
    Если юзер уже был – убедимся, что профиль существует.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)