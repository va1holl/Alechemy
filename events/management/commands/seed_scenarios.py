"""
Скрипт для заповнення бази даних сценаріями, коктейлями, челенджами та досягненнями.
Запуск: python manage.py seed_scenarios
"""
from django.core.management.base import BaseCommand
from decimal import Decimal


class Command(BaseCommand):
    help = 'Заповнює базу даних сценаріями, коктейлями, гейміфікацією'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Починаємо заповнення даними...'))
        
        self.create_scenarios()
        self.create_cocktails()
        self.create_challenges()
        self.create_achievements()
        
        self.stdout.write(self.style.SUCCESS('✅ Дані успішно створено!'))

    def create_scenarios(self):
        """Створюємо сценарії подій."""
        from events.models import Scenario, Drink
        
        scenarios_data = [
            {
                'slug': 'romantic-dinner',
                'name': 'Романтична вечеря',
                'description': 'Ідеальний вечір для двох. Свічки, музика, вино.',
                'category': 'romantic',
                'icon': '💕',
                'prep_text': 'Підготуйте свічки, музику та приємну атмосферу. Оберіть вино заздалегідь. Приготуйте легкі закуски.',
                'during_text': 'Насолоджуйтесь моментом. Не поспішайте з напоями. Спілкуйтесь, слухайте партнера.',
                'after_text': 'Випийте води перед сном. Насолодіться вечором! Не забудьте прибрати свічки.',
                'drinks': ['chardonnay', 'pinot-noir', 'prosecco', 'rose-wine', 'brut-champagne'],
            },
            {
                'slug': 'football-night',
                'name': 'Футбольний вечір',
                'description': 'Переглядаємо матч з друзями. Пиво, снеки, емоції.',
                'category': 'sport',
                'icon': '⚽',
                'prep_text': 'Запасіться пивом та снеками. Підготуйте великий екран. Запросіть друзів заздалегідь.',
                'during_text': 'Темп помірний. Не забувайте про закуски між напоями. Пийте воду.',
                'after_text': 'Не сідайте за кермо. Випийте води перед сном. Замовте таксі друзям.',
                'drinks': ['heineken', 'corona-extra', 'stella-artois', 'guinness', 'pilsner-urquell'],
            },
            {
                'slug': 'house-party',
                'name': 'Домашня вечірка',
                'description': 'Запрошуємо друзів додому. Музика, танці, веселощі.',
                'category': 'party',
                'icon': '🎉',
                'prep_text': 'Підготуйте різноманітні напої на будь-який смак. Приготуйте закуски. Створіть плейлист.',
                'during_text': 'Слідкуйте за гостями. Пропонуйте воду та їжу. Контролюйте гучність після 22:00.',
                'after_text': 'Не відпускайте гостей за кермо. Запропонуйте таксі. Приберіть небезпечні предмети.',
                'drinks': ['absolut-vodka', 'jack-daniels', 'bacardi-white', 'captain-morgan-spiced', 'jagermeister', 'aperol'],
            },
            {
                'slug': 'budget-evening',
                'name': 'Перед зарплатою',
                'description': 'Економний варіант вечора. Простіше, але не менш весело.',
                'category': 'budget',
                'icon': '💰',
                'prep_text': 'Оберіть доступні напої. Приготуйте прості закуски вдома. Запросіть близьких друзів.',
                'during_text': 'Насолоджуйтесь компанією, а не кількістю. Головне — спілкування.',
                'after_text': 'Економія = більше можливостей наступного разу! Записуйте витрати.',
                'drinks': ['heineken', 'corona-extra', 'absolut-vodka', 'red-dry-wine', 'apple-cider'],
            },
            {
                'slug': 'friends-gathering',
                'name': 'Зустріч друзів',
                'description': 'Посидіти з друзями за розмовами. Тепла атмосфера.',
                'category': 'friends',
                'icon': '👥',
                'prep_text': 'Запросіть близьких друзів. Підготуйте настільні ігри. Зробіть затишну атмосферу.',
                'during_text': 'Головне — спілкування. Напої — лише доповнення. Грайте в ігри.',
                'after_text': 'Домовтесь про наступну зустріч! Обміняйтесь фото з вечора.',
                'drinks': ['jameson', 'jack-daniels', 'guinness', 'craft-ipa', 'cabernet-sauvignon'],
            },
            {
                'slug': 'first-date',
                'name': 'Перше побачення',
                'description': 'Знайомство ближче. Легкі напої, приємна розмова.',
                'category': 'romantic',
                'icon': '💝',
                'prep_text': 'Оберіть затишне місце. Легкі напої — найкращий вибір. Будьте собою.',
                'during_text': 'Не перепивайте. Слухайте співрозмовника. Будьте уважні та ввічливі.',
                'after_text': 'Провідте партнера/партнерку. Напишіть, що вам було приємно.',
                'drinks': ['prosecco', 'rose-wine', 'aperol', 'martini-bianco', 'chardonnay'],
            },
            {
                'slug': 'birthday-party',
                'name': 'День народження',
                'description': 'Святкуємо день народження! Торт, подарунки, веселощі.',
                'category': 'celebration',
                'icon': '🎂',
                'prep_text': 'Замовте торт. Підготуйте подарунки. Прикрасьте приміщення. Запросіть гостей.',
                'during_text': 'Привітайте іменинника. Слідкуйте за гостями. Фотографуйте моменти.',
                'after_text': 'Подякуйте гостям. Допоможіть прибрати. Збережіть спогади.',
                'drinks': ['brut-champagne', 'prosecco', 'aperol', 'baileys-original', 'cointreau'],
            },
            {
                'slug': 'new-year-eve',
                'name': 'Новий рік',
                'description': 'Зустрічаємо Новий рік! Шампанське, феєрверки, побажання.',
                'category': 'celebration',
                'icon': '🎆',
                'prep_text': 'Підготуйте шампанське. Прикрасьте ялинку. Приготуйте святкові страви.',
                'during_text': 'Зустріньте опівніч з бокалом шампанського. Загадайте бажання. Обніміть близьких.',
                'after_text': 'Не запускайте феєрверки у нетверезому стані. Безпечного святкування!',
                'drinks': ['brut-champagne', 'moet-chandon', 'veuve-clicquot', 'prosecco', 'martini-asti'],
            },
            {
                'slug': 'summer-bbq',
                'name': 'Літнє барбекю',
                'description': 'Смажимо м\'ясо на свіжому повітрі. Літо, друзі, природа.',
                'category': 'outdoor',
                'icon': '🍖',
                'prep_text': 'Підготуйте гриль та вугілля. Замаринуйте м\'ясо. Візьміть напої в термосумці.',
                'during_text': 'Слідкуйте за вогнем. Чергуйте напої з водою. Не забувайте про сонцезахист.',
                'after_text': 'Загасіть вугілля повністю. Приберіть за собою. Не залишайте сміття.',
                'drinks': ['corona-extra', 'heineken', 'apple-cider', 'rose-wine', 'lemonade'],
            },
            {
                'slug': 'wine-tasting',
                'name': 'Дегустація вина',
                'description': 'Вивчаємо різні сорти вин. Культурний вечір.',
                'category': 'education',
                'icon': '🍷',
                'prep_text': 'Підготуйте 5-7 різних вин. Наріжте сир та хліб. Підготуйте картки з описом.',
                'during_text': 'Пробуйте маленькими ковтками. Записуйте враження. Не змішуйте з іншим алкоголем.',
                'after_text': 'Випийте води. Запишіть улюблені сорти. Сплануйте наступну дегустацію.',
                'drinks': ['cabernet-sauvignon', 'merlot-wine', 'pinot-noir', 'chardonnay', 'sauvignon-blanc', 'riesling'],
            },
        ]
        
        created = 0
        for scenario_data in scenarios_data:
            drink_slugs = scenario_data.pop('drinks')
            
            scenario, was_created = Scenario.objects.update_or_create(
                slug=scenario_data['slug'],
                defaults=scenario_data
            )
            
            if drink_slugs:
                drinks = Drink.objects.filter(slug__in=drink_slugs)
                scenario.drinks.add(*drinks)
            
            if was_created:
                created += 1
        
        self.stdout.write(f'  ✓ Сценаріїв: {len(scenarios_data)} (нових: {created})')

    def create_cocktails(self):
        """Створюємо коктейлі."""
        from recipes.models import Cocktail, CocktailIngredient
        from events.models import Ingredient
        
        cocktails_data = [
            # Класичні
            {
                'slug': 'mojito',
                'name': 'Мохіто',
                'description': 'Освіжаючий кубинський коктейль з білим ромом, лаймом та м\'ятою.',
                'category': 'long',
                'strength': 'medium',
                'instructions': '''1. Покладіть листя м\'яти та цукор у склянку.
2. Додайте сік лайма та злегка подавіть.
3. Додайте білий ром та перемішайте.
4. Наповніть склянку льодом.
5. Долийте содовою та прикрасьте м\'ятою.''',
                'is_active': True,
                'ingredients': [
                    ('М\'ята', 10, 'g'),
                    ('Лайм', 1, 'pcs'),
                    ('Цукор', 15, 'g'),
                    ('Содова', 100, 'ml'),
                    ('Лід', 150, 'g'),
                ],
            },
            {
                'slug': 'cuba-libre',
                'name': 'Куба Лібре',
                'description': 'Класичний ром з колою та лаймом. Простий і смачний.',
                'category': 'long',
                'strength': 'medium',
                'instructions': '''1. Наповніть склянку льодом.
2. Вичавіть сік лайма.
3. Додайте ром.
4. Долийте колою та обережно перемішайте.
5. Прикрасьте часточкою лайма.''',
                'is_active': True,
                'ingredients': [
                    ('Кола', 150, 'ml'),
                    ('Лайм', 0.5, 'pcs'),
                    ('Лід', 150, 'g'),
                ],
            },
            {
                'slug': 'margarita',
                'name': 'Маргарита',
                'description': 'Мексиканський коктейль з текілою, лаймом та апельсиновим лікером.',
                'category': 'short',
                'strength': 'strong',
                'instructions': '''1. Протріть край келиха лаймом та обмакніть у сіль.
2. Наповніть шейкер льодом.
3. Додайте текілу, лаймовий сік та лікер.
4. Добре струсіть.
5. Процідіть у келих.''',
                'is_active': True,
                'ingredients': [
                    ('Лайм', 1, 'pcs'),
                    ('Сіль', 3, 'g'),
                    ('Лід', 100, 'g'),
                ],
            },
            {
                'slug': 'pina-colada',
                'name': 'Піна Колада',
                'description': 'Тропічний коктейль з ромом, кокосом та ананасом.',
                'category': 'long',
                'strength': 'medium',
                'instructions': '''1. Змішайте ром, кокосові вершки та ананасовий сік у блендері.
2. Додайте лід та збийте.
3. Налийте у високий келих.
4. Прикрасьте ананасом та вишнею.''',
                'is_active': True,
                'ingredients': [
                    ('Вершки', 60, 'ml'),
                    ('Лід', 150, 'g'),
                ],
            },
            {
                'slug': 'cosmopolitan',
                'name': 'Космополітен',
                'description': 'Елегантний коктейль з горілкою, журавлиновим соком та лаймом.',
                'category': 'short',
                'strength': 'strong',
                'instructions': '''1. Наповніть шейкер льодом.
2. Додайте горілку, журавлиновий сік та лаймовий сік.
3. Добре струсіть.
4. Процідіть у коктейльний келих.
5. Прикрасьте цедрою лайма.''',
                'is_active': True,
                'ingredients': [
                    ('Журавлиний сік', 30, 'ml'),
                    ('Лайм', 0.5, 'pcs'),
                    ('Лід', 100, 'g'),
                ],
            },
            {
                'slug': 'whiskey-sour',
                'name': 'Віскі Сауер',
                'description': 'Класичний кислий коктейль з віскі та лимонним соком.',
                'category': 'short',
                'strength': 'strong',
                'instructions': '''1. Наповніть шейкер льодом.
2. Додайте віскі, лимонний сік та цукровий сироп.
3. Добре струсіть.
4. Процідіть у склянку з льодом.
5. Прикрасьте вишнею та апельсином.''',
                'is_active': True,
                'ingredients': [
                    ('Лимон', 1, 'pcs'),
                    ('Цукор', 20, 'g'),
                    ('Лід', 100, 'g'),
                ],
            },
            {
                'slug': 'long-island',
                'name': 'Лонг Айленд',
                'description': 'Міцний коктейль з декількома видами алкоголю. Не для новачків.',
                'category': 'long',
                'strength': 'very_strong',
                'instructions': '''1. Наповніть склянку льодом.
2. Додайте горілку, ром, джин, текілу та лікер.
3. Вичавіть лимонний сік.
4. Долийте колою.
5. Обережно перемішайте.''',
                'is_active': True,
                'ingredients': [
                    ('Лимон', 0.5, 'pcs'),
                    ('Кола', 50, 'ml'),
                    ('Лід', 150, 'g'),
                ],
            },
            {
                'slug': 'gin-tonic',
                'name': 'Джин-тонік',
                'description': 'Класичний британський коктейль. Простий та освіжаючий.',
                'category': 'long',
                'strength': 'medium',
                'instructions': '''1. Наповніть склянку льодом.
2. Налийте джин.
3. Долийте тоніком у пропорції 1:2.
4. Обережно перемішайте.
5. Прикрасьте часточкою лайма або огірком.''',
                'is_active': True,
                'ingredients': [
                    ('Тонік', 150, 'ml'),
                    ('Лайм', 0.25, 'pcs'),
                    ('Лід', 150, 'g'),
                ],
            },
            {
                'slug': 'aperol-spritz',
                'name': 'Апероль Шпріц',
                'description': 'Італійський аперитив. Легкий, освіжаючий, гіркуватий.',
                'category': 'long',
                'strength': 'light',
                'instructions': '''1. Наповніть келих льодом.
2. Налийте Апероль.
3. Додайте просекко.
4. Долийте содовою.
5. Прикрасьте часточкою апельсина.''',
                'is_active': True,
                'ingredients': [
                    ('Апельсин', 0.25, 'pcs'),
                    ('Содова', 30, 'ml'),
                    ('Лід', 100, 'g'),
                ],
            },
            {
                'slug': 'negroni',
                'name': 'Негроні',
                'description': 'Класичний італійський коктейль. Гіркий, насичений.',
                'category': 'short',
                'strength': 'strong',
                'instructions': '''1. Наповніть склянку льодом.
2. Додайте джин, вермут та Кампарі у рівних пропорціях.
3. Перемішайте барною ложкою.
4. Прикрасьте цедрою апельсина.''',
                'is_active': True,
                'ingredients': [
                    ('Апельсин', 0.25, 'pcs'),
                    ('Лід', 100, 'g'),
                ],
            },
            # Безалкогольні
            {
                'slug': 'virgin-mojito',
                'name': 'Безалкогольний Мохіто',
                'description': 'Освіжаючий коктейль без алкоголю. Ідеальний для всіх.',
                'category': 'long',
                'strength': 'non_alcoholic',
                'instructions': '''1. Покладіть листя м\'яти та цукор у склянку.
2. Додайте сік лайма та злегка подавіть.
3. Наповніть льодом.
4. Долийте содовою.
5. Прикрасьте м\'ятою та лаймом.''',
                'is_active': True,
                'ingredients': [
                    ('М\'ята', 10, 'g'),
                    ('Лайм', 1, 'pcs'),
                    ('Цукор', 15, 'g'),
                    ('Содова', 150, 'ml'),
                    ('Лід', 150, 'g'),
                ],
            },
            {
                'slug': 'shirley-temple',
                'name': 'Ширлі Темпл',
                'description': 'Класичний безалкогольний коктейль для всієї родини.',
                'category': 'long',
                'strength': 'non_alcoholic',
                'instructions': '''1. Наповніть склянку льодом.
2. Налийте імбирний ель.
3. Додайте гренадин.
4. Обережно перемішайте.
5. Прикрасьте вишнею.''',
                'is_active': True,
                'ingredients': [
                    ('Лід', 150, 'g'),
                ],
            },
        ]
        
        created = 0
        for cocktail_data in cocktails_data:
            ingredients = cocktail_data.pop('ingredients')
            
            cocktail, was_created = Cocktail.objects.update_or_create(
                slug=cocktail_data['slug'],
                defaults=cocktail_data
            )
            
            if was_created:
                created += 1
                
                # Додаємо інгредієнти
                for ing_name, amount, unit in ingredients:
                    try:
                        ingredient = Ingredient.objects.get(name=ing_name)
                        CocktailIngredient.objects.get_or_create(
                            cocktail=cocktail,
                            ingredient=ingredient,
                            defaults={'amount': Decimal(str(amount)), 'unit': unit}
                        )
                    except Ingredient.DoesNotExist:
                        pass
        
        self.stdout.write(f'  ✓ Коктейлів: {len(cocktails_data)} (нових: {created})')

    def create_challenges(self):
        """Створюємо челенджі."""
        from gamification.models import Challenge
        
        challenges_data = [
            {
                'code': 'first_event',
                'title': 'Перша подія',
                'description': 'Створіть свою першу подію',
                'difficulty': 'easy',
                'points_reward': 50,
                'target_count': 1,
                'icon': '🎯',
            },
            {
                'code': 'three_events',
                'title': 'Тричі — це система',
                'description': 'Створіть 3 події',
                'difficulty': 'medium',
                'points_reward': 150,
                'target_count': 3,
                'icon': '📅',
            },
            {
                'code': 'ten_events',
                'title': 'Досвідчений організатор',
                'description': 'Створіть 10 подій',
                'difficulty': 'hard',
                'points_reward': 500,
                'target_count': 10,
                'icon': '🏆',
            },
            {
                'code': 'diary_master',
                'title': 'Майстер щоденника',
                'description': 'Зробіть 10 записів у щоденнику',
                'difficulty': 'medium',
                'points_reward': 200,
                'target_count': 10,
                'icon': '📝',
            },
            {
                'code': 'cocktail_lover',
                'title': 'Любитель коктейлів',
                'description': 'Спробуйте 5 різних коктейлів',
                'difficulty': 'hard',
                'points_reward': 300,
                'target_count': 5,
                'icon': '🍸',
            },
            {
                'code': 'social_butterfly',
                'title': 'Душа компанії',
                'description': 'Запросіть 5 друзів на події',
                'difficulty': 'hard',
                'points_reward': 250,
                'target_count': 5,
                'icon': '👥',
            },
            {
                'code': 'wine_connoisseur',
                'title': 'Знавець вин',
                'description': 'Проведіть дегустацію вина',
                'difficulty': 'medium',
                'points_reward': 150,
                'target_count': 1,
                'icon': '🍷',
            },
            {
                'code': 'responsible_host',
                'title': 'Відповідальний господар',
                'description': 'Завершіть 5 подій без інцидентів',
                'difficulty': 'medium',
                'points_reward': 200,
                'target_count': 5,
                'icon': '🏠',
            },
            {
                'code': 'recipe_explorer',
                'title': 'Дослідник рецептів',
                'description': 'Переглянуть 10 рецептів коктейлів',
                'difficulty': 'easy',
                'points_reward': 75,
                'target_count': 10,
                'icon': '📖',
            },
            {
                'code': 'shopping_pro',
                'title': 'Майстер закупівель',
                'description': 'Створіть 3 списки покупок',
                'difficulty': 'easy',
                'points_reward': 100,
                'target_count': 3,
                'icon': '🛒',
            },
        ]
        
        created = 0
        for challenge_data in challenges_data:
            obj, was_created = Challenge.objects.update_or_create(
                code=challenge_data['code'],
                defaults=challenge_data
            )
            if was_created:
                created += 1
        
        self.stdout.write(f'  ✓ Челенджів: {len(challenges_data)} (нових: {created})')

    def create_achievements(self):
        """Створюємо досягнення."""
        from gamification.models import Achievement
        
        achievements_data = [
            {
                'code': 'welcome',
                'title': 'Ласкаво просимо!',
                'description': 'Зареєструвались в Alechemy',
                'points_reward': 10,
            },
            {
                'code': 'first_event_completed',
                'title': 'Перший досвід',
                'description': 'Завершили першу подію',
                'points_reward': 50,
            },
            {
                'code': 'week_streak',
                'title': 'Тижнева серія',
                'description': 'Заходили в додаток 7 днів поспіль',
                'points_reward': 100,
            },
            {
                'code': 'month_streak',
                'title': 'Місячна серія',
                'description': 'Заходили в додаток 30 днів поспіль',
                'points_reward': 500,
            },
            {
                'code': 'responsible_drinker',
                'title': 'Відповідальний підхід',
                'description': 'Заповнили профіль з вагою',
                'points_reward': 30,
            },
            {
                'code': 'first_cocktail',
                'title': 'Перший коктейль',
                'description': 'Приготували перший коктейль за рецептом',
                'points_reward': 40,
            },
            {
                'code': 'party_master',
                'title': 'Майстер вечірок',
                'description': 'Провели 10 успішних подій',
                'points_reward': 300,
            },
            {
                'code': 'social_star',
                'title': 'Соціальна зірка',
                'description': 'Запросили 10 друзів',
                'points_reward': 200,
            },
            {
                'code': 'explorer',
                'title': 'Дослідник',
                'description': 'Спробували всі типи сценаріїв',
                'points_reward': 250,
            },
            {
                'code': 'gourmet',
                'title': 'Гурман',
                'description': 'Приготували 5 різних страв',
                'points_reward': 150,
            },
        ]
        
        created = 0
        for achievement_data in achievements_data:
            obj, was_created = Achievement.objects.update_or_create(
                code=achievement_data['code'],
                defaults=achievement_data
            )
            if was_created:
                created += 1
        
        self.stdout.write(f'  ✓ Досягнень: {len(achievements_data)} (нових: {created})')
