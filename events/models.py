from decimal import Decimal
from django.utils import timezone

from django.conf import settings
from django.db import models


class DrinkCategory(models.Model):
    """
    Категория напитка: вино, пиво, крепкое, безалкогольное и т.п.
    Хранится в БД, чтобы можно было добавлять новые категории без правки кода.
    """
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class DrinkTag(models.Model):
    """
    Теги напитка: 'красное', 'сухое', 'игристое', 'яблочное', 'кола' и т.п.
    Для фильтрации и рекомендаций.
    """
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Drink(models.Model):
    class Strength(models.TextChoices):
        STRONG = "strong", "Крепкий"
        REGULAR = "regular", "Обычный"
        NON_ALCOHOLIC = "non_alcoholic", "Безалкогольный"

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    category = models.ForeignKey(
        DrinkCategory,
        on_delete=models.PROTECT,
        related_name="drinks",
        null=True,
        blank=True,
    )
    strength = models.CharField(
        max_length=20,
        choices=Strength.choices,
        default=Strength.REGULAR,
    )
    abv = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Крепость в % об.",
    )
    tags = models.ManyToManyField(
        DrinkTag,
        related_name="drinks",
        blank=True,
    )

    def __str__(self) -> str:
        return self.name


class Dish(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Очень просто"
        MEDIUM = "medium", "Средне"
        HARD = "hard", "Посложнее"

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    recipe_text = models.TextField(
        blank=True,
        help_text="Короткий рецепт или инструкция для этого блюда.",
    )
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
    )
    drinks = models.ManyToManyField("events.Drink", related_name="dishes", blank=True)

    def __str__(self) -> str:
        return self.name


class Scenario(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # какие напитки доступны в этом сценарии
    drinks = models.ManyToManyField("events.Drink", related_name="scenarios", blank=True)

    # НОВОЕ: текст по этапам
    prep_text = models.TextField(
        blank=True,
        help_text="Рекомендации по подготовке: що купити, що підготувати, атмосфера.",
    )
    during_text = models.TextField(
        blank=True,
        help_text="Що робити під час події: теми розмов, темп пиття, ритм вечора.",
    )
    after_text = models.TextField(
        blank=True,
        help_text="Відновлення: сон, вода, поїсти, не сідати за кермо тощо.",
    )

    def __str__(self) -> str:
        return self.name


class Event(models.Model):
    class Intensity(models.TextChoices):
        LOW = "low", "Спокойно"
        MEDIUM = "medium", "Нормально"
        HIGH = "high", "Жёстко"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events",
    )
    scenario = models.ForeignKey(
        Scenario,
        on_delete=models.PROTECT,
        related_name="events",
    )

    drink = models.ForeignKey(
        Drink,
        on_delete=models.PROTECT,
        related_name="events",
        null=True,
        blank=True,
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.SET_NULL,
        related_name="events",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=150, blank=True)
    date = models.DateField()
    people_count = models.PositiveIntegerField(default=2)
    duration_hours = models.PositiveIntegerField(default=2)
    intensity = models.CharField(
        max_length=10,
        choices=Intensity.choices,
        default=Intensity.MEDIUM,
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        base = self.title or self.scenario.name
        return f"{base} ({self.date})"

    class Meta:
        ordering = ["-date", "-created_at"]


class AlcoholLog(models.Model):
    """
    Запись в алко-дневник:
    - что выпил,
    - сколько,
    - когда,
    - примерная оценка BAC.
    Всё очень грубо и только для ориентировочного отображения в приложении.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="alcohol_logs",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alcohol_logs",
        help_text="Можно привязать запись к событию, а можно оставить пустым.",
    )
    drink = models.ForeignKey(
        Drink,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alcohol_logs",
    )

    taken_at = models.DateTimeField(
        default=timezone.now,
        help_text="Когда примерно был напиток.",
    )
    volume_ml = models.PositiveIntegerField(
        help_text="Объём напитка в миллилитрах, например 150.",
    )

    # Если не указать, берём abv из Drink
    abv = models.DecimalField(
        "Крепость, % об.",
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
    )

    bac_estimate = models.DecimalField(
        "Оценка BAC, ‰",
        max_digits=5,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Очень грубая оценка по одной порции, только для справки.",
    )

    note = models.CharField(
        max_length=255,
        blank=True,
        help_text="Опциональный комментарий.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-taken_at", "-created_at"]

    def __str__(self) -> str:
        base = self.drink.name if self.drink else "Напиток"
        return f"{base} {self.volume_ml} мл @ {self.taken_at:%Y-%m-%d %H:%M}"

    # === расчёт BAC ===

    def _get_weight_and_sex(self):
        """
        Пытаемся аккуратно вытащить вес/пол из профиля.
        Поля могут называться по-разному — тут максимально мягко.
        """
        profile = getattr(self.user, "profile", None)
        if not profile:
            return None, None

        weight = (
            getattr(profile, "weight_kg", None)
            or getattr(profile, "weight", None)
        )
        sex = getattr(profile, "sex", None) or getattr(profile, "gender", None)

        return weight, sex

    def calculate_bac(self) -> Decimal | None:
        """
        Очень приблизительная оценка BAC для одной порции.
        Никаких мед. выводов, просто цифра в интерфейсе.
        """
        if not self.volume_ml:
            return None

        # крепость
        abv = self.abv
        if abv is None and self.drink and self.drink.abv is not None:
            abv = self.drink.abv

        if abv is None:
            return None

        weight_kg, sex = self._get_weight_and_sex()

        if not weight_kg:
            # без веса пользователя считать нечего
            return None

        try:
            weight_kg = float(weight_kg)
        except (TypeError, ValueError):
            return None

        if weight_kg <= 0:
            return None

        # коэффициент распределения (Widmark r)
        sex_str = (str(sex) or "").lower()
        if sex_str in ("m", "male", "man", "ч", "м"):
            r = 0.68
        elif sex_str in ("f", "female", "woman", "ж"):
            r = 0.55
        else:
            r = 0.6  # усреднённое

        # объём чистого спирта в граммах
        # 1 мл напитка * (abv/100) * 0.789 (плотность этанола)
        pure_alcohol_g = float(self.volume_ml) * float(abv) / 100.0 * 0.789

        # Widmark: BAC (г/дл) ≈ A / (r * weight_kg * 10)
        bac = pure_alcohol_g / (r * weight_kg * 10.0)

        # переводим в промилле (‰): 0.08 -> 0.8‰
        bac_promille = bac * 10.0

        return Decimal(str(round(bac_promille, 3)))

    def save(self, *args, **kwargs):
        self.bac_estimate = self.calculate_bac()
        super().save(*args, **kwargs)