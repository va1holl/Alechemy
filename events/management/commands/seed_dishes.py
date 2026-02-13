"""
Скрипт для заповнення бази даних стравами та закусками.
Запуск: python manage.py seed_dishes
"""
from django.core.management.base import BaseCommand
from decimal import Decimal


class Command(BaseCommand):
    help = 'Заповнює базу даних стравами та закусками для різних напоїв'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Починаємо заповнення стравами...'))
        
        self.create_ingredients()
        self.create_dishes()
        
        self.stdout.write(self.style.SUCCESS('✅ Страви успішно створено!'))

    def create_ingredients(self):
        """Створюємо базові інгредієнти."""
        from events.models import Ingredient, IngredientCategory, IngredientUnit
        
        ingredients = [
            # М'ясо та риба
            ('Курка', IngredientCategory.FOOD, IngredientUnit.G),
            ('Свинина', IngredientCategory.FOOD, IngredientUnit.G),
            ('Яловичина', IngredientCategory.FOOD, IngredientUnit.G),
            ('Бекон', IngredientCategory.FOOD, IngredientUnit.G),
            ('Креветки', IngredientCategory.FOOD, IngredientUnit.G),
            ('Лосось', IngredientCategory.FOOD, IngredientUnit.G),
            ('Тунець', IngredientCategory.FOOD, IngredientUnit.G),
            ('Анчоуси', IngredientCategory.FOOD, IngredientUnit.G),
            
            # Овочі
            ('Картопля', IngredientCategory.FOOD, IngredientUnit.G),
            ('Цибуля', IngredientCategory.FOOD, IngredientUnit.PCS),
            ('Часник', IngredientCategory.FOOD, IngredientUnit.G),
            ('Помідори', IngredientCategory.FOOD, IngredientUnit.G),
            ('Огірки', IngredientCategory.FOOD, IngredientUnit.G),
            ('Перець болгарський', IngredientCategory.FOOD, IngredientUnit.PCS),
            ('Оливки', IngredientCategory.FOOD, IngredientUnit.G),
            ('Каперси', IngredientCategory.FOOD, IngredientUnit.G),
            ('Авокадо', IngredientCategory.FOOD, IngredientUnit.PCS),
            ('Салат', IngredientCategory.FOOD, IngredientUnit.G),
            ('Руккола', IngredientCategory.FOOD, IngredientUnit.G),
            ('Шпинат', IngredientCategory.FOOD, IngredientUnit.G),
            ('Халапеньо', IngredientCategory.FOOD, IngredientUnit.G),
            
            # Сири
            ('Сир Фета', IngredientCategory.FOOD, IngredientUnit.G),
            ('Сир Пармезан', IngredientCategory.FOOD, IngredientUnit.G),
            ('Сир Моцарела', IngredientCategory.FOOD, IngredientUnit.G),
            ('Сир Чеддер', IngredientCategory.FOOD, IngredientUnit.G),
            ('Сир Камамбер', IngredientCategory.FOOD, IngredientUnit.G),
            ('Сир Горгонзола', IngredientCategory.FOOD, IngredientUnit.G),
            ('Сир Брі', IngredientCategory.FOOD, IngredientUnit.G),
            
            # Хліб та випічка
            ('Багет', IngredientCategory.FOOD, IngredientUnit.G),
            ('Хліб тостовий', IngredientCategory.FOOD, IngredientUnit.PCS),
            ('Чіпси тортилья', IngredientCategory.FOOD, IngredientUnit.G),
            ('Крекери', IngredientCategory.FOOD, IngredientUnit.G),
            
            # Зелень та спеції
            ('Базилік', IngredientCategory.FOOD, IngredientUnit.G),
            ('Петрушка', IngredientCategory.FOOD, IngredientUnit.G),
            ('Кінза', IngredientCategory.FOOD, IngredientUnit.G),
            ('М\'ята', IngredientCategory.FOOD, IngredientUnit.G),
            ('Розмарин', IngredientCategory.FOOD, IngredientUnit.G),
            ('Орегано', IngredientCategory.FOOD, IngredientUnit.G),
            ('Сіль', IngredientCategory.FOOD, IngredientUnit.G),
            ('Чорний перець', IngredientCategory.FOOD, IngredientUnit.G),
            ('Паприка', IngredientCategory.FOOD, IngredientUnit.G),
            ('Кумін', IngredientCategory.FOOD, IngredientUnit.G),
            
            # Соуси та олія
            ('Оливкова олія', IngredientCategory.FOOD, IngredientUnit.ML),
            ('Вершкове масло', IngredientCategory.FOOD, IngredientUnit.G),
            ('Соєвий соус', IngredientCategory.FOOD, IngredientUnit.ML),
            ('Бальзамік', IngredientCategory.FOOD, IngredientUnit.ML),
            ('Гірчиця', IngredientCategory.FOOD, IngredientUnit.G),
            ('Майонез', IngredientCategory.FOOD, IngredientUnit.G),
            ('Сметана', IngredientCategory.FOOD, IngredientUnit.G),
            ('Соус Тар-тар', IngredientCategory.FOOD, IngredientUnit.G),
            ('Соус BBQ', IngredientCategory.FOOD, IngredientUnit.ML),
            ('Гуакамоле', IngredientCategory.FOOD, IngredientUnit.G),
            ('Сальса', IngredientCategory.FOOD, IngredientUnit.G),
            
            # Фрукти
            ('Лимон', IngredientCategory.FOOD, IngredientUnit.PCS),
            ('Лайм', IngredientCategory.FOOD, IngredientUnit.PCS),
            ('Апельсин', IngredientCategory.FOOD, IngredientUnit.PCS),
            ('Яблуко', IngredientCategory.FOOD, IngredientUnit.PCS),
            ('Виноград', IngredientCategory.FOOD, IngredientUnit.G),
            ('Інжир', IngredientCategory.FOOD, IngredientUnit.PCS),
            ('Манго', IngredientCategory.FOOD, IngredientUnit.PCS),
            
            # Горіхи
            ('Мигдаль', IngredientCategory.FOOD, IngredientUnit.G),
            ('Волоські горіхи', IngredientCategory.FOOD, IngredientUnit.G),
            ('Арахіс', IngredientCategory.FOOD, IngredientUnit.G),
            ('Кеш\'ю', IngredientCategory.FOOD, IngredientUnit.G),
            
            # Інше
            ('Яйця', IngredientCategory.FOOD, IngredientUnit.PCS),
            ('Мед', IngredientCategory.FOOD, IngredientUnit.G),
            ('Цукор', IngredientCategory.FOOD, IngredientUnit.G),
            ('Вершки', IngredientCategory.FOOD, IngredientUnit.ML),
            ('Хумус', IngredientCategory.FOOD, IngredientUnit.G),
            ('Тахіні', IngredientCategory.FOOD, IngredientUnit.G),
            
            # Для коктейлів
            ('Лід', IngredientCategory.OTHER, IngredientUnit.G),
            ('Содова', IngredientCategory.OTHER, IngredientUnit.ML),
            ('Тонік', IngredientCategory.OTHER, IngredientUnit.ML),
            ('Кола', IngredientCategory.OTHER, IngredientUnit.ML),
            ('Апельсиновий сік', IngredientCategory.OTHER, IngredientUnit.ML),
            ('Журавлиний сік', IngredientCategory.OTHER, IngredientUnit.ML),
        ]
        
        created = 0
        for name, category, unit in ingredients:
            obj, was_created = Ingredient.objects.get_or_create(
                name=name,
                defaults={'category': category, 'default_unit': unit}
            )
            if was_created:
                created += 1
        
        self.stdout.write(f'  ✓ Інгредієнтів: {len(ingredients)} (нових: {created})')

    def create_dishes(self):
        """Створюємо страви та прив'язуємо до напоїв."""
        from events.models import Dish, DishIngredient, Ingredient, Drink, IngredientUnit
        
        dishes_data = [
            # ==================== ДО ВИНА ====================
            {
                'slug': 'greek-salad',
                'name': 'Грецький салат',
                'description': 'Класичний середземноморський салат з фетою, оливками та свіжими овочами',
                'recipe_text': '''1. Наріжте помідори та огірки великими кубиками.
2. Наріжте перець соломкою.
3. Додайте оливки та кубики фети.
4. Заправте оливковою олією, посоліть та поперчіть.
5. Посипте орегано та подавайте.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Помідори', 200, IngredientUnit.G),
                    ('Огірки', 150, IngredientUnit.G),
                    ('Перець болгарський', 1, IngredientUnit.PCS),
                    ('Сир Фета', 100, IngredientUnit.G),
                    ('Оливки', 50, IngredientUnit.G),
                    ('Цибуля', 0.5, IngredientUnit.PCS),
                    ('Оливкова олія', 30, IngredientUnit.ML),
                    ('Орегано', 2, IngredientUnit.G),
                ],
                'drinks': ['chardonnay', 'sauvignon-blanc', 'white-dry-wine', 'rose-wine'],
            },
            {
                'slug': 'bruschetta-tomato',
                'name': 'Брускета з томатами',
                'description': 'Італійська закуска на хрусткому хлібі з часником та свіжими томатами',
                'recipe_text': '''1. Наріжте багет скибочками та підсушіть у духовці.
2. Натріть кожну скибочку часником.
3. Наріжте помідори дрібними кубиками.
4. Змішайте помідори з базиліком та оливковою олією.
5. Викладіть суміш на хліб, посоліть.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Багет', 100, IngredientUnit.G),
                    ('Помідори', 200, IngredientUnit.G),
                    ('Часник', 5, IngredientUnit.G),
                    ('Базилік', 10, IngredientUnit.G),
                    ('Оливкова олія', 20, IngredientUnit.ML),
                    ('Сіль', 2, IngredientUnit.G),
                ],
                'drinks': ['prosecco', 'brut-champagne', 'white-dry-wine', 'red-dry-wine'],
            },
            {
                'slug': 'cheese-plate-wine',
                'name': 'Сирна тарілка до вина',
                'description': 'Вишукана підбірка сирів з фруктами та горіхами',
                'recipe_text': '''1. Дістаньте сири з холодильника за 30 хв до подачі.
2. Наріжте сири різними способами.
3. Викладіть на дерев\'яну дошку.
4. Додайте виноград, інжир та мед.
5. Прикрасьте волоськими горіхами.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Сир Брі', 50, IngredientUnit.G),
                    ('Сир Камамбер', 50, IngredientUnit.G),
                    ('Сир Горгонзола', 40, IngredientUnit.G),
                    ('Сир Пармезан', 40, IngredientUnit.G),
                    ('Виноград', 100, IngredientUnit.G),
                    ('Інжир', 2, IngredientUnit.PCS),
                    ('Волоські горіхи', 30, IngredientUnit.G),
                    ('Мед', 20, IngredientUnit.G),
                ],
                'drinks': ['cabernet-sauvignon', 'merlot-wine', 'pinot-noir', 'red-dry-wine'],
            },
            {
                'slug': 'carpaccio-beef',
                'name': 'Карпачо з яловичини',
                'description': 'Тонко нарізана сира яловичина з рукколою та пармезаном',
                'recipe_text': '''1. Заморозьте яловичину на 30 хв для легшого нарізання.
2. Наріжте м\'ясо тонкими слайсами.
3. Викладіть на тарілку, додайте рукколу.
4. Посипте стружкою пармезану.
5. Полийте оливковою олією та бальзаміком.''',
                'difficulty': 'medium',
                'ingredients': [
                    ('Яловичина', 150, IngredientUnit.G),
                    ('Руккола', 30, IngredientUnit.G),
                    ('Сир Пармезан', 30, IngredientUnit.G),
                    ('Оливкова олія', 20, IngredientUnit.ML),
                    ('Бальзамік', 10, IngredientUnit.ML),
                    ('Каперси', 10, IngredientUnit.G),
                ],
                'drinks': ['pinot-noir', 'cabernet-sauvignon', 'merlot-wine'],
            },
            
            # ==================== ДО ПИВА ====================
            {
                'slug': 'chicken-wings-bbq',
                'name': 'Курячі крильця BBQ',
                'description': 'Хрусткі курячі крильця в соусі барбекю',
                'recipe_text': '''1. Замаринуйте крильця в спеціях на 1 годину.
2. Запікайте при 200°C 40 хвилин.
3. Полийте соусом BBQ.
4. Запікайте ще 10 хвилин до карамелізації.
5. Подавайте з соусом для макання.''',
                'difficulty': 'medium',
                'ingredients': [
                    ('Курка', 500, IngredientUnit.G),
                    ('Соус BBQ', 100, IngredientUnit.ML),
                    ('Часник', 5, IngredientUnit.G),
                    ('Паприка', 5, IngredientUnit.G),
                    ('Сіль', 3, IngredientUnit.G),
                    ('Чорний перець', 2, IngredientUnit.G),
                ],
                'drinks': ['lager-beer', 'craft-ipa', 'pilsner-beer', 'wheat-beer'],
            },
            {
                'slug': 'nachos-supreme',
                'name': 'Начос Супрім',
                'description': 'Хрусткі тортилья чіпси з сиром, сальсою та гуакамоле',
                'recipe_text': '''1. Викладіть чіпси на деко.
2. Посипте тертим чеддером.
3. Запікайте 5 хв до розплавлення сиру.
4. Додайте сальсу, гуакамоле та сметану.
5. Посипте халапеньо та кінзою.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Чіпси тортилья', 150, IngredientUnit.G),
                    ('Сир Чеддер', 100, IngredientUnit.G),
                    ('Гуакамоле', 80, IngredientUnit.G),
                    ('Сальса', 80, IngredientUnit.G),
                    ('Сметана', 50, IngredientUnit.G),
                    ('Халапеньо', 20, IngredientUnit.G),
                    ('Кінза', 10, IngredientUnit.G),
                ],
                'drinks': ['lager-beer', 'craft-ipa', 'wheat-beer'],
            },
            {
                'slug': 'loaded-fries',
                'name': 'Картопля фрі з начинкою',
                'description': 'Хрустка картопля з беконом, сиром та соусами',
                'recipe_text': '''1. Приготуйте картоплю фрі (заморожену або свіжу).
2. Обсмажте бекон до хрусткості.
3. Викладіть фрі, посипте сиром.
4. Додайте подрібнений бекон.
5. Полийте соусами та подавайте гарячою.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Картопля', 300, IngredientUnit.G),
                    ('Бекон', 80, IngredientUnit.G),
                    ('Сир Чеддер', 60, IngredientUnit.G),
                    ('Сметана', 40, IngredientUnit.G),
                    ('Петрушка', 5, IngredientUnit.G),
                ],
                'drinks': ['dark-stout', 'lager-beer', 'belgian-ale'],
            },
            {
                'slug': 'beer-cheese-dip',
                'name': 'Пивний сирний дip',
                'description': 'Гарячий сирний соус з пивом для макання',
                'recipe_text': '''1. Розтопіть масло на сковороді.
2. Додайте борошно, перемішайте.
3. Повільно влийте пиво та вершки.
4. Додайте тертий сир, перемішуйте до однорідності.
5. Подавайте з хлібом або кренделями.''',
                'difficulty': 'medium',
                'ingredients': [
                    ('Сир Чеддер', 200, IngredientUnit.G),
                    ('Вершки', 100, IngredientUnit.ML),
                    ('Вершкове масло', 30, IngredientUnit.G),
                    ('Гірчиця', 10, IngredientUnit.G),
                    ('Багет', 150, IngredientUnit.G),
                ],
                'drinks': ['dark-stout', 'belgian-ale', 'wheat-beer', 'porter-beer'],
            },
            
            # ==================== ДО ВІСКІ ====================
            {
                'slug': 'smoked-salmon-toast',
                'name': 'Тости з копченим лососем',
                'description': 'Хрусткі тости з вершковим сиром та копченим лососем',
                'recipe_text': '''1. Підсушіть хліб до хрусткості.
2. Намажте вершковим сиром.
3. Покладіть скибочки копченого лосося.
4. Прикрасьте кропом та каперсами.
5. Видавіть трохи лимонного соку.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Хліб тостовий', 2, IngredientUnit.PCS),
                    ('Лосось', 100, IngredientUnit.G),
                    ('Сметана', 40, IngredientUnit.G),
                    ('Каперси', 10, IngredientUnit.G),
                    ('Лимон', 0.25, IngredientUnit.PCS),
                ],
                'drinks': ['jameson', 'jack-daniels', 'chivas-regal-12', 'johnnie-walker-black'],
            },
            {
                'slug': 'beef-tartare',
                'name': 'Тартар з яловичини',
                'description': 'Класичний тартар з сирої яловичини зі спеціями',
                'recipe_text': '''1. Дрібно наріжте яловичину ножем.
2. Додайте каперси, корнішони, цибулю.
3. Заправте оливковою олією, гірчицею.
4. Сформуйте порції, зробіть заглиблення.
5. Покладіть яєчний жовток, подавайте з тостами.''',
                'difficulty': 'hard',
                'ingredients': [
                    ('Яловичина', 200, IngredientUnit.G),
                    ('Яйця', 1, IngredientUnit.PCS),
                    ('Каперси', 15, IngredientUnit.G),
                    ('Цибуля', 0.25, IngredientUnit.PCS),
                    ('Гірчиця', 10, IngredientUnit.G),
                    ('Оливкова олія', 15, IngredientUnit.ML),
                    ('Хліб тостовий', 2, IngredientUnit.PCS),
                ],
                'drinks': ['glenfiddich-12', 'johnnie-walker-black'],
            },
            {
                'slug': 'dark-chocolate-truffles',
                'name': 'Шоколадні трюфелі',
                'description': 'Домашні шоколадні трюфелі з какао',
                'recipe_text': '''1. Розтопіть шоколад з вершками.
2. Охолодіть до загустіння.
3. Сформуйте кульки.
4. Обваляйте в какао-порошку.
5. Охолодіть перед подачею.''',
                'difficulty': 'medium',
                'ingredients': [
                    ('Вершки', 100, IngredientUnit.ML),
                    ('Вершкове масло', 20, IngredientUnit.G),
                ],
                'drinks': ['hennessy-vs', 'remy-martin-vsop', 'courvoisier-vs'],
            },
            
            # ==================== ДО РОМУ ====================
            {
                'slug': 'coconut-shrimp',
                'name': 'Креветки в кокосовій паніровці',
                'description': 'Хрусткі креветки з тропічним соусом',
                'recipe_text': '''1. Очистіть креветки, залиште хвостики.
2. Обваляйте у борошні, потім у яйці.
3. Запаніруйте в кокосовій стружці.
4. Обсмажте у фритюрі до золотистого кольору.
5. Подавайте з солодким чилі соусом.''',
                'difficulty': 'medium',
                'ingredients': [
                    ('Креветки', 200, IngredientUnit.G),
                    ('Яйця', 1, IngredientUnit.PCS),
                    ('Лайм', 0.5, IngredientUnit.PCS),
                ],
                'drinks': ['bacardi-white', 'captain-morgan-spiced', 'havana-club-7', 'malibu-rum'],
            },
            {
                'slug': 'jerk-chicken-bites',
                'name': 'Курка Джерк',
                'description': 'Пікантна ямайська курка зі спеціями',
                'recipe_text': '''1. Змішайте спеції для джерк маринаду.
2. Замаринуйте курку на 2-4 години.
3. Запікайте або смажте на грилі.
4. Наріжте на шматочки.
5. Подавайте з лаймом та свіжою зеленню.''',
                'difficulty': 'medium',
                'ingredients': [
                    ('Курка', 400, IngredientUnit.G),
                    ('Часник', 10, IngredientUnit.G),
                    ('Халапеньо', 15, IngredientUnit.G),
                    ('Лайм', 1, IngredientUnit.PCS),
                    ('Кінза', 10, IngredientUnit.G),
                ],
                'drinks': ['captain-morgan-spiced', 'havana-club-7', 'diplomatico-rum'],
            },
            
            # ==================== ДО ТЕКІЛИ ====================
            {
                'slug': 'guacamole-fresh',
                'name': 'Свіже гуакамоле',
                'description': 'Класичне мексиканське гуакамоле з авокадо',
                'recipe_text': '''1. Розім\'яйте авокадо виделкою.
2. Додайте дрібно нарізану цибулю та помідори.
3. Додайте сік лайма та кінзу.
4. Посоліть за смаком.
5. Подавайте з чіпсами тортилья.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Авокадо', 2, IngredientUnit.PCS),
                    ('Помідори', 100, IngredientUnit.G),
                    ('Цибуля', 0.25, IngredientUnit.PCS),
                    ('Лайм', 1, IngredientUnit.PCS),
                    ('Кінза', 15, IngredientUnit.G),
                    ('Халапеньо', 10, IngredientUnit.G),
                    ('Чіпси тортилья', 100, IngredientUnit.G),
                ],
                'drinks': ['jose-cuervo-gold', 'patron-silver', 'don-julio-blanco', 'olmeca-gold'],
            },
            {
                'slug': 'fish-tacos',
                'name': 'Тако з рибою',
                'description': 'Мексиканські тако з хрусткою рибою та капустою',
                'recipe_text': '''1. Запаніруйте рибу та обсмажте.
2. Наріжте капусту тонкою соломкою.
3. Приготуйте соус з майонезу та лайму.
4. Підігрійте тортильї.
5. Зберіть тако: тортилья, риба, капуста, соус.''',
                'difficulty': 'medium',
                'ingredients': [
                    ('Тунець', 200, IngredientUnit.G),
                    ('Салат', 100, IngredientUnit.G),
                    ('Майонез', 40, IngredientUnit.G),
                    ('Лайм', 1, IngredientUnit.PCS),
                    ('Кінза', 10, IngredientUnit.G),
                ],
                'drinks': ['jose-cuervo-gold', 'patron-silver', 'lager-beer', 'craft-ipa'],
            },
            
            # ==================== ДО ДЖИНУ ====================
            {
                'slug': 'cucumber-sandwiches',
                'name': 'Сендвічі з огірком',
                'description': 'Елегантні англійські сендвічі для чаювання',
                'recipe_text': '''1. Наріжте огірки тонкими слайсами.
2. Намажте хліб вершковим сиром.
3. Покладіть огірки, посоліть та поперчіть.
4. Накрийте другим шматком хліба.
5. Обріжте скоринки, наріжте на трикутники.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Хліб тостовий', 4, IngredientUnit.PCS),
                    ('Огірки', 150, IngredientUnit.G),
                    ('Сметана', 60, IngredientUnit.G),
                    ('Сіль', 2, IngredientUnit.G),
                    ('Чорний перець', 1, IngredientUnit.G),
                ],
                'drinks': ['tanqueray-gin', 'bombay-sapphire', 'hendricks-gin', 'gordon-gin'],
            },
            {
                'slug': 'shrimp-cocktail',
                'name': 'Коктейль з креветок',
                'description': 'Класична закуска з креветок з пікантним соусом',
                'recipe_text': '''1. Відваріть креветки, охолодіть.
2. Приготуйте соус: кетчуп, хрін, лимон.
3. Викладіть креветки на лід.
4. Подавайте з соусом у центрі.
5. Прикрасьте лимоном та зеленню.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Креветки', 250, IngredientUnit.G),
                    ('Лимон', 0.5, IngredientUnit.PCS),
                    ('Петрушка', 10, IngredientUnit.G),
                ],
                'drinks': ['tanqueray-gin', 'bombay-sapphire', 'hendricks-gin', 'beefeater-gin'],
            },
            
            # ==================== ДО ГОРІЛКИ ====================
            {
                'slug': 'pickles-assorted',
                'name': 'Асорті солінь',
                'description': 'Традиційна слов\'янська закуска до горілки',
                'recipe_text': '''1. Охолодіть соління.
2. Красиво викладіть на тарілку.
3. Додайте маринований часник.
4. Прикрасьте кропом.
5. Подавайте холодним.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Огірки', 150, IngredientUnit.G),
                    ('Помідори', 100, IngredientUnit.G),
                    ('Часник', 20, IngredientUnit.G),
                ],
                'drinks': ['absolut-vodka', 'finlandia-vodka', 'grey-goose', 'beluga-vodka', 'smirnoff-vodka'],
            },
            {
                'slug': 'salo-with-garlic',
                'name': 'Сало з часником',
                'description': 'Традиційна українська закуска',
                'recipe_text': '''1. Наріжте сало тонкими скибочками.
2. Викладіть на тарілку.
3. Додайте подрібнений часник.
4. Посипте чорним перцем.
5. Подавайте з чорним хлібом.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Свинина', 150, IngredientUnit.G),
                    ('Часник', 15, IngredientUnit.G),
                    ('Багет', 100, IngredientUnit.G),
                    ('Чорний перець', 2, IngredientUnit.G),
                ],
                'drinks': ['absolut-vodka', 'finlandia-vodka', 'nemiroff-honey-pepper', 'khortytsia-vodka'],
            },
            
            # ==================== УНІВЕРСАЛЬНІ ====================
            {
                'slug': 'mixed-nuts',
                'name': 'Мікс горіхів',
                'description': 'Асорті смажених горіхів з сіллю та спеціями',
                'recipe_text': '''1. Змішайте різні горіхи.
2. Підсмажте на сухій сковороді.
3. Додайте сіль та паприку.
4. Охолодіть.
5. Подавайте в декоративній мисці.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Мигдаль', 50, IngredientUnit.G),
                    ('Кеш\'ю', 50, IngredientUnit.G),
                    ('Арахіс', 50, IngredientUnit.G),
                    ('Сіль', 3, IngredientUnit.G),
                    ('Паприка', 2, IngredientUnit.G),
                ],
                'drinks': ['jameson', 'lager-beer', 'craft-ipa', 'jack-daniels', 'absolut-vodka'],
            },
            {
                'slug': 'hummus-veggies',
                'name': 'Хумус з овочами',
                'description': 'Ближньосхідний хумус зі свіжими овочами',
                'recipe_text': '''1. Викладіть хумус у глибоку тарілку.
2. Зробіть заглиблення, налийте оливкової олії.
3. Посипте паприкою.
4. Наріжте овочі соломкою.
5. Подавайте овочі навколо хумусу.''',
                'difficulty': 'easy',
                'ingredients': [
                    ('Хумус', 150, IngredientUnit.G),
                    ('Огірки', 100, IngredientUnit.G),
                    ('Перець болгарський', 1, IngredientUnit.PCS),
                    ('Оливкова олія', 15, IngredientUnit.ML),
                    ('Паприка', 2, IngredientUnit.G),
                ],
                'drinks': ['sauvignon-blanc', 'rose-wine', 'tanqueray', 'aperol'],
            },
        ]
        
        created = 0
        updated = 0
        images_loaded = 0
        
        for dish_data in dishes_data:
            ingredients = dish_data.pop('ingredients')
            drink_slugs = dish_data.pop('drinks')
            
            dish, was_created = Dish.objects.update_or_create(
                slug=dish_data['slug'],
                defaults=dish_data
            )
            
            if was_created:
                created += 1
            else:
                updated += 1
            
            # Завантажуємо зображення якщо ще немає
            if not dish.image:
                if self.download_dish_image(dish):
                    images_loaded += 1
            
            # Очищаємо та додаємо інгредієнти
            DishIngredient.objects.filter(dish=dish).delete()
            for ing_name, qty, unit in ingredients:
                try:
                    ingredient = Ingredient.objects.get(name=ing_name)
                    DishIngredient.objects.create(
                        dish=dish,
                        ingredient=ingredient,
                        qty_per_person=Decimal(str(qty)),
                        unit=unit
                    )
                except Ingredient.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ Інгредієнт не знайдено: {ing_name}')
                    )
            
            # Прив'язуємо напої
            drinks = Drink.objects.filter(slug__in=drink_slugs)
            dish.drinks.set(drinks)
        
        self.stdout.write(f'  ✓ Страв: {len(dishes_data)} (нових: {created}, оновлено: {updated}, зображень: {images_loaded})')
    
    def download_dish_image(self, dish):
        """Завантажуємо зображення для страви з TheMealDB."""
        import requests
        from django.core.files.base import ContentFile
        
        # Прямі URL для типових страв
        dish_images = {
            'bruschetta': 'https://www.themealdb.com/images/media/meals/1520084413.jpg',  # Bruschetta
            'caprese': 'https://www.themealdb.com/images/media/meals/k29viq1585565980.jpg',  # Caprese
            'greek-salad': 'https://www.themealdb.com/images/media/meals/k29viq1585565980.jpg',  # Salad
            'caesar-salad': 'https://www.themealdb.com/images/media/meals/k29viq1585565980.jpg',  # Salad
            'cheese-platter': 'https://www.themealdb.com/images/media/meals/sytuqu1511553755.jpg',  # Cheese
            'meat-platter': 'https://www.themealdb.com/images/media/meals/1548772327.jpg',  # Meat
            'hummus': 'https://www.themealdb.com/images/media/meals/wuxrtu1483564410.jpg',  # Falafel
            'guacamole': 'https://www.themealdb.com/images/media/meals/1529444830.jpg',  # Mexican
            'nachos': 'https://www.themealdb.com/images/media/meals/1529444830.jpg',  # Nachos
            'chicken-wings': 'https://www.themealdb.com/images/media/meals/rwuyqx1507025522.jpg',  # Chicken
            'shrimp-cocktail': 'https://www.themealdb.com/images/media/meals/1529445434.jpg',  # Shrimp
            'salmon-tartare': 'https://www.themealdb.com/images/media/meals/1548772327.jpg',  # Salmon
            'beef-carpaccio': 'https://www.themealdb.com/images/media/meals/bc8v651619789840.jpg',  # Beef
            'grilled-vegetables': 'https://www.themealdb.com/images/media/meals/hqaejl1695738653.jpg',  # Vegetables
            'french-fries': 'https://www.themealdb.com/images/media/meals/sxysrt1468240488.jpg',  # Fries
            'onion-rings': 'https://www.themealdb.com/images/media/meals/sxysrt1468240488.jpg',  # Fried
            'mozzarella-sticks': 'https://www.themealdb.com/images/media/meals/sytuqu1511553755.jpg',  # Cheese
            'spring-rolls': 'https://www.themealdb.com/images/media/meals/1525876468.jpg',  # Spring Rolls
            'tacos': 'https://www.themealdb.com/images/media/meals/ypxvwv1505333929.jpg',  # Tacos
            'sliders': 'https://www.themealdb.com/images/media/meals/k420tj1585565244.jpg',  # Burger
            'pizza-margherita': 'https://www.themealdb.com/images/media/meals/x0lk931587671540.jpg',  # Pizza
        }
        
        image_url = dish_images.get(dish.slug)
        
        if image_url:
            try:
                img_response = requests.get(image_url, timeout=15)
                if img_response.status_code == 200:
                    filename = f'{dish.slug}.jpg'
                    dish.image.save(filename, ContentFile(img_response.content), save=True)
                    return True
            except Exception:
                pass
        
        # Fallback - пошук в TheMealDB
        try:
            api_url = f'https://www.themealdb.com/api/json/v1/1/random.php'
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('meals') and len(data['meals']) > 0:
                    image_url = data['meals'][0].get('strMealThumb')
                    if image_url:
                        img_response = requests.get(image_url, timeout=15)
                        if img_response.status_code == 200:
                            filename = f'{dish.slug}.jpg'
                            dish.image.save(filename, ContentFile(img_response.content), save=True)
                            return True
        except Exception:
            pass
        
        return False
