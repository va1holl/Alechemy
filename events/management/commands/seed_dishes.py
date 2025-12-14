from decimal import Decimal
from django.core.management.base import BaseCommand

from events.models import Dish, Ingredient, DishIngredient, IngredientUnit, Drink, Scenario


class Command(BaseCommand):
    help = "Сид: сценарий 'Первое свидание' + Белое сухое вино + 2 блюда с ингредиентами (для shopping)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Удалить ранее созданные этим сидом объекты и создать заново",
        )

    def handle(self, *args, **kwargs):
        reset = kwargs["reset"]

        # --- constants ---
        WINE_SLUG = "white-dry-wine"
        WINE_NAME = "Белое сухое вино"

        SCENARIO_SLUG = "first-date"
        SCENARIO_NAME = "Первое свидание"

        DISHES = [
            {
                "slug": "bruschetta-tomato-basil",
                "name": "Брускетта с томатами и базиликом",
                "recipe_text": (
                    "Подсушить хлеб. Натереть чесноком. "
                    "Смешать томаты с базиликом и маслом, посолить. Выложить на хлеб."
                ),
                "ingredients": [
                    ("Багет", IngredientUnit.G, Decimal("80")),
                    ("Помидоры", IngredientUnit.G, Decimal("150")),
                    ("Базилик", IngredientUnit.G, Decimal("5")),
                    ("Оливковое масло", IngredientUnit.ML, Decimal("15")),
                    ("Чеснок", IngredientUnit.G, Decimal("2")),
                    ("Соль", IngredientUnit.G, Decimal("2")),
                ],
            },
            {
                "slug": "garlic-shrimp",
                "name": "Креветки в чесночном масле",
                "recipe_text": (
                    "Обжарить чеснок в масле, добавить креветки, быстро довести до готовности. "
                    "Соль/перец, лимон по вкусу, зелень в конце."
                ),
                "ingredients": [
                    ("Креветки", IngredientUnit.G, Decimal("150")),
                    ("Сливочное масло", IngredientUnit.G, Decimal("20")),
                    ("Чеснок", IngredientUnit.G, Decimal("4")),
                    ("Лимон", IngredientUnit.PCS, Decimal("0.25")),
                    ("Петрушка", IngredientUnit.G, Decimal("5")),
                    ("Соль", IngredientUnit.G, Decimal("2")),
                    ("Чёрный перец", IngredientUnit.G, Decimal("1")),
                ],
            },
        ]

        # --- reset (аккуратно, только то, что этот сид создаёт) ---
        if reset:
            dish_slugs = [d["slug"] for d in DISHES]

            # удаляем ингредиенты блюд (связи), потом блюда, потом сценарий/вино
            DishIngredient.objects.filter(dish__slug__in=dish_slugs).delete()
            Dish.objects.filter(slug__in=dish_slugs).delete()

            # сценарий (может быть связан с Event, поэтому delete может быть запрещён)
            try:
                Scenario.objects.filter(slug=SCENARIO_SLUG).delete()
            except Exception:
                pass

            Drink.objects.filter(slug=WINE_SLUG).delete()

            # удаляем ингредиенты только если они нигде больше не используются
            names = {name for d in DISHES for (name, _, _) in d["ingredients"]}
            for n in names:
                try:
                    ing = Ingredient.objects.get(name=n)
                except Ingredient.DoesNotExist:
                    continue
                if not DishIngredient.objects.filter(ingredient=ing).exists():
                    ing.delete()

            self.stdout.write(self.style.WARNING("RESET: удалены объекты этого сида."))

        # --- wine ---
        wine, _ = Drink.objects.update_or_create(
            slug=WINE_SLUG,
            defaults={"name": WINE_NAME},
        )

        # если у Drink есть поле крепости/ABV или тип, попробуем заполнить (без фанатизма)
        for field, value in [
            ("abv", Decimal("12.0")),
            ("strength", Decimal("12.0")),
            ("kind", "wine"),
        ]:
            if hasattr(wine, field):
                try:
                    setattr(wine, field, value)
                    wine.save(update_fields=[field])
                except Exception:
                    pass

        # --- scenario ---
        scenario_defaults = {
            "name": SCENARIO_NAME,
            "prep_text": "Лёгкий план: музыка, простые закуски, вода рядом. Не усложняй.",
            "during_text": "Держи темп спокойным, чередуй алкоголь с водой, не играй в героя.",
            "after_text": "Вода, лёгкая еда, сон. Утром никаких подвигов.",
            "description": "Сценарий для спокойного вечера без лишней суеты.",
        }

        scenario, _ = Scenario.objects.update_or_create(
            slug=SCENARIO_SLUG,
            defaults=scenario_defaults,
        )

        # привязка вина к сценарию (если у Scenario есть M2M drinks)
        if hasattr(scenario, "drinks"):
            try:
                scenario.drinks.add(wine)
            except Exception:
                pass

        # --- helper: поставить difficulty, если поле есть и требует choices ---
        def pick_difficulty_value():
            if not hasattr(Dish, "difficulty"):
                return None
            try:
                f = Dish._meta.get_field("difficulty")
            except Exception:
                return None
            choices = list(getattr(f, "choices", []) or [])
            if not choices:
                return None

            preferred = ["simple", "easy", "medium", "normal", "hard", "1", "2", "3"]
            values = [c[0] for c in choices]

            for p in preferred:
                if p in values:
                    return p
            return values[0] if values else None

        default_difficulty = pick_difficulty_value()

        # --- dishes + ingredients ---
        for d in DISHES:
            dish_defaults = {"name": d["name"], "recipe_text": d["recipe_text"]}

            if default_difficulty is not None and hasattr(Dish, "difficulty"):
                dish_defaults["difficulty"] = default_difficulty

            dish, _ = Dish.objects.update_or_create(
                slug=d["slug"],
                defaults=dish_defaults,
            )

            # привязка блюда к вину (поддержим M2M и FK)
            if hasattr(dish, "drinks"):
                try:
                    dish.drinks.add(wine)
                except Exception:
                    pass
            elif hasattr(dish, "drink_id"):
                try:
                    dish.drink = wine
                    dish.save(update_fields=["drink"])
                except Exception:
                    pass

            # ингредиенты (qty_per_person)
            for name, unit, qty in d["ingredients"]:
                ing, _ = Ingredient.objects.get_or_create(
                    name=name,
                    defaults={"default_unit": unit},
                )

                DishIngredient.objects.update_or_create(
                    dish=dish,
                    ingredient=ing,
                    unit=unit,
                    defaults={"qty_per_person": qty},
                )

        self.stdout.write(
            self.style.SUCCESS("Готово: сценарий 'Первое свидание', Белое сухое вино и 2 блюда с ингредиентами добавлены.")
        )