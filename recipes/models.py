from django.db import models
from django.conf import settings
from events.models import Ingredient


class CocktailCategory(models.TextChoices):
    """Категорії коктейлів для фільтрації."""
    SHOT = "shot", "Шот"
    CLASSIC = "classic", "Класичний"
    TIKI = "tiki", "Тікі"
    SOUR = "sour", "Сауер"
    FIZZ = "fizz", "Фіз"
    HIGHBALL = "highball", "Хайбол"
    MARTINI = "martini", "Мартіні"
    FROZEN = "frozen", "Заморожений"
    HOT = "hot", "Гарячий"
    PUNCH = "punch", "Пунш"
    SPRITZ = "spritz", "Шпріц"
    OTHER = "other", "Інше"


class CocktailStrength(models.TextChoices):
    """Міцність коктейлю."""
    LIGHT = "light", "Легкий (до 10%)"
    MEDIUM = "medium", "Середній (10-20%)"
    STRONG = "strong", "Міцний (20-30%)"
    VERY_STRONG = "very_strong", "Дуже міцний (30%+)"
    NON_ALCOHOLIC = "non_alcoholic", "Безалкогольний"


class Cocktail(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='cocktails/', blank=True, null=True)
    
    category = models.CharField(
        max_length=20,
        choices=CocktailCategory.choices,
        default=CocktailCategory.CLASSIC,
        help_text="Тип коктейлю"
    )
    strength = models.CharField(
        max_length=20,
        choices=CocktailStrength.choices,
        default=CocktailStrength.MEDIUM,
        help_text="Міцність коктейлю"
    )

    def __str__(self):
        return self.name
    
    @property
    def avg_rating(self):
        from django.db.models import Avg
        result = self.reviews.aggregate(avg=Avg('rating'))
        return result['avg'] or 0

class CocktailIngredient(models.Model):
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=8)

    def __str__(self):
        return f"{self.ingredient} ({self.amount} {self.unit}) in {self.cocktail}"


class CocktailReview(models.Model):
    """Відгук на коктейль."""
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)  # 1-5
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cocktail', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user} on {self.cocktail}"