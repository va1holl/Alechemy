from decimal import Decimal
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.conf import settings
from django.db import models


class DrinkCategory(models.Model):
    """
    Категорія напою: вино, пиво, міцне, безалкогольне тощо.
    Зберігається в БД, щоб можна було додавати нові категорії без правки коду.
    """
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class DrinkTag(models.Model):
    """
    Теги напою: 'червоне', 'сухе', 'ігристе', 'яблучне', 'кола' тощо.
    Для фільтрації та рекомендацій.
    """
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Drink(models.Model):
    class Strength(models.TextChoices):
        STRONG = "strong", "Міцний"
        REGULAR = "regular", "Звичайний"
        NON_ALCOHOLIC = "non_alcoholic", "Безалкогольний"

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
        help_text="Міцність у % об.",
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
        EASY = "easy", _("Дуже просто")
        MEDIUM = "medium", _("Середньо")
        HARD = "hard", _("Складніше")

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

    ingredients = models.ManyToManyField(
        "events.Ingredient",
        through="events.DishIngredient",
        related_name="dishes",
        blank=True,
    )

    def __str__(self) -> str:
        return self.name


class Scenario(models.Model):
    class Category(models.TextChoices):
        ROMANTIC = "romantic", "Побачення"
        SPORT = "sport", "Спорт/Футбол"
        PARTY = "party", "Вечірка"
        BUDGET = "budget", "Перед зарплатою"
        FRIENDS = "friends", "Друзі"
        FAMILY = "family", "Сімейне"
        HOLIDAY = "holiday", "Свято"
        OTHER = "other", "Інше"

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
        help_text="Категорія сценарію для фільтрації"
    )
    icon = models.CharField(max_length=10, default="🎉", help_text="Емодзі для відображення")

    # які напої доступні в цьому сценарії
    drinks = models.ManyToManyField("events.Drink", related_name="scenarios", blank=True)

    # НОВЕ: текст по етапах
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
        help_text="Основний напій (застаріле, використовуйте drinks)",
    )
    # Множинні напої
    drinks = models.ManyToManyField(
        Drink,
        related_name="multi_events",
        blank=True,
        help_text="Напої для події",
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.SET_NULL,
        related_name="events",
        null=True,
        blank=True,
        help_text="Основна страва (застаріле, використовуйте dishes)",
    )
    # Множинні страви
    dishes = models.ManyToManyField(
        Dish,
        related_name="multi_events",
        blank=True,
        help_text="Страви для події",
    )
    # Коктейлі з модуля recipes
    cocktails = models.ManyToManyField(
        "recipes.Cocktail",
        related_name="events",
        blank=True,
        help_text="Коктейлі для події",
    )

    title = models.CharField(max_length=150, blank=True)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True, help_text="Час початку події")
    end_time = models.TimeField(null=True, blank=True, help_text="Час закінчення події")
    people_count = models.PositiveIntegerField(default=2)
    duration_hours = models.PositiveIntegerField(default=2)
    intensity = models.CharField(
        max_length=10,
        choices=Intensity.choices,
        default=Intensity.MEDIUM,
    )
    notes = models.TextField(blank=True)
    
    # Локація події
    location_name = models.CharField(max_length=255, blank=True, help_text="Назва місця")
    location_address = models.CharField(max_length=500, blank=True, help_text="Адреса")
    location_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, help_text="Широта"
    )
    location_lng = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, help_text="Довгота"
    )
    
    # Фідбек після події
    is_finished = models.BooleanField(default=False, help_text="Подія завершена")
    user_rating = models.PositiveIntegerField(
        null=True, blank=True, 
        help_text="Оцінка події від 1 до 5"
    )
    feedback = models.TextField(blank=True, help_text="Відгук після події")
    feedback_submitted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        base = self.title or self.scenario.name
        return f"{base} ({self.date})"
    
    def get_participants(self):
        """Отримати список учасників події"""
        return self.event_participants.select_related('participant__profile').all()
    
    def get_average_rating(self):
        """Отримати середню оцінку від усіх учасників"""
        ratings = list(
            self.event_participants.filter(rating__isnull=False).values_list('rating', flat=True)
        )
        if self.user_rating:
            ratings.append(self.user_rating)
        return sum(ratings) / len(ratings) if ratings else None

    class Meta:
        ordering = ["-date", "-created_at"]


class EventParticipant(models.Model):
    """
    Учасники події - друзі, яких запросив власник події.
    """
    class Status(models.TextChoices):
        PENDING = "pending", "Очікує"
        ACCEPTED = "accepted", "Прийнято"
        DECLINED = "declined", "Відхилено"
        MAYBE = "maybe", "Можливо"
    
    class Role(models.TextChoices):
        HEAD = "head", "Глава"
        PARTICIPANT = "participant", "Учасник"
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="event_participants"
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_invitations"
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    role = models.CharField(
        max_length=15,
        choices=Role.choices,
        default=Role.PARTICIPANT
    )
    
    # Фідбек учасника
    rating = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Оцінка події від 1 до 5"
    )
    feedback = models.TextField(blank=True)
    feedback_submitted_at = models.DateTimeField(null=True, blank=True)
    
    invited_at = models.DateTimeField(auto_now_add=True, null=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ("event", "participant")
        ordering = ["-invited_at"]
    
    def __str__(self):
        return f"{self.participant.email} @ {self.event}"
    
    def accept(self):
        from django.utils import timezone
        self.status = self.Status.ACCEPTED
        self.responded_at = timezone.now()
        self.save()
    
    def decline(self):
        from django.utils import timezone
        self.status = self.Status.DECLINED
        self.responded_at = timezone.now()
        self.save()


class EventMessage(models.Model):
    """
    Повідомлення в обговоренні події.
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_messages"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["created_at"]
    
    def __str__(self):
        return f"{self.user.email} @ {self.event}: {self.text[:50]}"


class AlcoholLog(models.Model):
    """
    Запис в алко-щоденник:
    - що випив,
    - скільки,
    - коли,
    - приблизна оцінка BAC.
    Все дуже грубо і тільки для орієнтовного відображення в застосунку.
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
        help_text="Можна прив'язати запис до події, а можна залишити порожнім.",
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
        help_text="Коли приблизно був напій.",
    )
    volume_ml = models.PositiveIntegerField(
        help_text="Об'єм напою в мілілітрах, наприклад 150.",
    )

    # Якщо не вказати, беремо abv з Drink
    abv = models.DecimalField(
        "Міцність, % об.",
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
    )

    bac_estimate = models.DecimalField(
        "Оцінка BAC, ‰",
        max_digits=5,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Дуже груба оцінка по одній порції, тільки для довідки.",
    )

    note = models.CharField(
        max_length=255,
        blank=True,
        help_text="Опціональний коментар.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-taken_at", "-created_at"]

    def __str__(self) -> str:
        base = self.drink.name if self.drink else "Напій"
        return f"{base} {self.volume_ml} мл @ {self.taken_at:%Y-%m-%d %H:%M}"

    # === розрахунок BAC ===

    def _get_weight_and_sex(self):
        """
        Намагаємось акуратно витягнути вагу/стать з профілю.
        Поля можуть називатися по-різному — тут максимально м'яко.
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
        Дуже приблизна оцінка BAC для однієї порції.
        Жодних мед. висновків, просто цифра в інтерфейсі.
        """
        if not self.volume_ml:
            return None

        # міцність
        abv = self.abv
        if abv is None and self.drink and self.drink.abv is not None:
            abv = self.drink.abv

        if abv is None:
            return None

        weight_kg, sex = self._get_weight_and_sex()

        if not weight_kg:
            # без ваги користувача рахувати нічого
            return None

        try:
            weight_kg = float(weight_kg)
        except (TypeError, ValueError):
            return None

        if weight_kg <= 0:
            return None

        # коефіцієнт розподілу (Widmark r)
        sex_str = (str(sex) or "").lower()
        if sex_str in ("m", "male", "man", "ч", "м"):
            r = 0.68
        elif sex_str in ("f", "female", "woman", "ж"):
            r = 0.55
        else:
            r = 0.6  # усереднене

        # об'єм чистого спирту в грамах
        # 1 мл напою * (abv/100) * 0.789 (щільність етанолу)
        pure_alcohol_g = float(self.volume_ml) * float(abv) / 100.0 * 0.789

        # Widmark: BAC (г/дл) ≈ A / (r * weight_kg * 10)
        bac = pure_alcohol_g / (r * weight_kg * 10.0)

        # переводимо в проміле (‰): 0.08 -> 0.8‰
        bac_promille = bac * 10.0

        return Decimal(str(round(bac_promille, 3)))

    def save(self, *args, **kwargs):
        self.bac_estimate = self.calculate_bac()
        super().save(*args, **kwargs)


class IngredientUnit(models.TextChoices):
    PCS = "pcs", "шт"
    G = "g", "г"
    KG = "kg", "кг"
    ML = "ml", "мл"
    L = "l", "л"


class IngredientCategory(models.TextChoices):
    FOOD = "food", "Їжа"
    OTHER = "other", "Інше"


class Ingredient(models.Model):
    name = models.CharField(max_length=120, unique=True)
    category = models.CharField(
        max_length=16,
        choices=IngredientCategory.choices,
        default=IngredientCategory.FOOD,
    )
    default_unit = models.CharField(
        max_length=8,
        choices=IngredientUnit.choices,
        default=IngredientUnit.G,
    )
    is_alcoholic = models.BooleanField(default=False, verbose_name="Алкогольний")

    def __str__(self) -> str:
        return self.name


class DishIngredient(models.Model):
    """
    Кількість інгредієнта на 1 людину (на порцію).
    """
    dish = models.ForeignKey("events.Dish", on_delete=models.CASCADE, related_name="dish_ingredients")
    ingredient = models.ForeignKey("events.Ingredient", on_delete=models.PROTECT, related_name="dish_uses")

    qty_per_person = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal("0.0"))
    unit = models.CharField(max_length=8, choices=IngredientUnit.choices, default=IngredientUnit.G)

    class Meta:
        unique_together = ("dish", "ingredient", "unit")

    def __str__(self) -> str:
        return f"{self.dish}: {self.ingredient} {self.qty_per_person} {self.unit}"