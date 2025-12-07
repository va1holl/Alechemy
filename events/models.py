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
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.EASY,
    )
    # M2M к Drink внутри того же приложения
    drinks = models.ManyToManyField("Drink", related_name="dishes", blank=True)

    def __str__(self) -> str:
        return self.name


class Scenario(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # какие напитки доступны в этом сценарии
    drinks = models.ManyToManyField("Drink", related_name="scenarios", blank=True)

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