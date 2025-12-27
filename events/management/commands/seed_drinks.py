"""
Скрипт для заповнення бази даних алкогольними та безалкогольними напоями.
Запуск: python manage.py seed_drinks
"""
from django.core.management.base import BaseCommand
from decimal import Decimal


class Command(BaseCommand):
    help = 'Заповнює базу даних напоями (алкоголь та безалкогольні)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Починаємо заповнення напоями...'))
        
        self.create_categories()
        self.create_tags()
        self.create_drinks()
        self.link_drinks_to_scenarios()
        
        self.stdout.write(self.style.SUCCESS('✅ Напої успішно створено!'))

    def create_categories(self):
        """Створюємо категорії напоїв."""
        from events.models import DrinkCategory
        
        categories = [
            ('vodka', 'Горілка'),
            ('whiskey', 'Віскі'),
            ('rum', 'Ром'),
            ('gin', 'Джин'),
            ('tequila', 'Текіла'),
            ('cognac', 'Коньяк / Бренді'),
            ('liqueur', 'Лікери'),
            ('wine', 'Вино'),
            ('champagne', 'Шампанське / Ігристе'),
            ('beer', 'Пиво'),
            ('cider', 'Сидр'),
            ('vermouth', 'Вермут'),
            ('aperitif', 'Аперитиви'),
            ('non-alcoholic', 'Безалкогольні'),
        ]
        
        created = 0
        for slug, name in categories:
            obj, was_created = DrinkCategory.objects.get_or_create(
                slug=slug,
                defaults={'name': name}
            )
            if was_created:
                created += 1
        
        self.stdout.write(f'  ✓ Категорій: {len(categories)} (нових: {created})')

    def create_tags(self):
        """Створюємо теги для напоїв."""
        from events.models import DrinkTag
        
        tags = [
            ('premium', 'Преміум'),
            ('budget', 'Бюджетний'),
            ('classic', 'Класика'),
            ('sweet', 'Солодкий'),
            ('dry', 'Сухий'),
            ('sparkling', 'Ігристий'),
            ('aged', 'Витриманий'),
            ('craft', 'Крафтовий'),
            ('fruit', 'Фруктовий'),
            ('herbal', 'Трав\'яний'),
            ('spicy', 'Пряний'),
            ('smoky', 'Димний'),
            ('light', 'Легкий'),
            ('strong', 'Міцний'),
        ]
        
        created = 0
        for slug, name in tags:
            obj, was_created = DrinkTag.objects.get_or_create(
                slug=slug,
                defaults={'name': name}
            )
            if was_created:
                created += 1
        
        self.stdout.write(f'  ✓ Тегів: {len(tags)} (нових: {created})')

    def create_drinks(self):
        """Створюємо напої."""
        from events.models import Drink, DrinkCategory, DrinkTag
        
        # Отримуємо категорії
        categories = {c.slug: c for c in DrinkCategory.objects.all()}
        tags = {t.slug: t for t in DrinkTag.objects.all()}
        
        drinks_data = [
            # Горілка
            {
                'slug': 'absolut-vodka',
                'name': 'Absolut Vodka',
                'description': 'Шведська преміум горілка з пшениці. Чистий, м\'який смак.',
                'category': 'vodka',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium', 'classic'],
            },
            {
                'slug': 'nemiroff-honey-pepper',
                'name': 'Nemiroff Медова з перцем',
                'description': 'Українська горілка з медом та перцем. М\'який смак з гострим післясмаком.',
                'category': 'vodka',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['classic', 'spicy'],
            },
            {
                'slug': 'grey-goose',
                'name': 'Grey Goose',
                'description': 'Французька преміум горілка. Елегантний, витончений смак.',
                'category': 'vodka',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium'],
            },
            
            # Віскі
            {
                'slug': 'jack-daniels',
                'name': 'Jack Daniel\'s',
                'description': 'Американський теннессійський віскі. Карамель, ваніль, дуб.',
                'category': 'whiskey',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['classic', 'smoky'],
            },
            {
                'slug': 'jameson',
                'name': 'Jameson',
                'description': 'Ірландський віскі потрійної дистиляції. М\'який, солодкуватий.',
                'category': 'whiskey',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['classic', 'light'],
            },
            {
                'slug': 'johnnie-walker-black',
                'name': 'Johnnie Walker Black Label',
                'description': 'Шотландський купажований віскі 12 років витримки. Димний, насичений.',
                'category': 'whiskey',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium', 'aged', 'smoky'],
            },
            {
                'slug': 'makers-mark',
                'name': 'Maker\'s Mark',
                'description': 'Кентуккійський бурбон. Солодкий, з нотами карамелі та ванілі.',
                'category': 'whiskey',
                'strength': 'strong',
                'abv': Decimal('45.0'),
                'tags': ['premium', 'sweet'],
            },
            
            # Ром
            {
                'slug': 'bacardi-white',
                'name': 'Bacardi Carta Blanca',
                'description': 'Білий кубинський ром. Легкий, ідеальний для коктейлів.',
                'category': 'rum',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['classic', 'light'],
            },
            {
                'slug': 'captain-morgan-spiced',
                'name': 'Captain Morgan Spiced Gold',
                'description': 'Карибський пряний ром. Ваніль, спеції, карамель.',
                'category': 'rum',
                'strength': 'strong',
                'abv': Decimal('35.0'),
                'tags': ['spicy', 'sweet'],
            },
            {
                'slug': 'havana-club-7',
                'name': 'Havana Club 7 Años',
                'description': 'Кубинський темний ром 7 років витримки. Насичений, тропічний.',
                'category': 'rum',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium', 'aged'],
            },
            
            # Джин
            {
                'slug': 'gordon-gin',
                'name': 'Gordon\'s London Dry Gin',
                'description': 'Класичний лондонський сухий джин. Ялівець, цитрус.',
                'category': 'gin',
                'strength': 'strong',
                'abv': Decimal('37.5'),
                'tags': ['classic', 'dry'],
            },
            {
                'slug': 'bombay-sapphire',
                'name': 'Bombay Sapphire',
                'description': 'Преміум джин з 10 ботанічними інгредієнтами. Складний, елегантний.',
                'category': 'gin',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium', 'herbal'],
            },
            {
                'slug': 'hendricks-gin',
                'name': 'Hendrick\'s Gin',
                'description': 'Шотландський джин з огірком та трояндою. Унікальний, освіжаючий.',
                'category': 'gin',
                'strength': 'strong',
                'abv': Decimal('41.4'),
                'tags': ['premium', 'herbal'],
            },
            
            # Текіла
            {
                'slug': 'jose-cuervo-gold',
                'name': 'Jose Cuervo Especial Gold',
                'description': 'Мексиканська золота текіла. Агава, дуб, ваніль.',
                'category': 'tequila',
                'strength': 'strong',
                'abv': Decimal('38.0'),
                'tags': ['classic'],
            },
            {
                'slug': 'patron-silver',
                'name': 'Patrón Silver',
                'description': 'Преміум біла текіла. Чистий смак агави, цитрусові ноти.',
                'category': 'tequila',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium', 'light'],
            },
            
            # Коньяк / Бренді
            {
                'slug': 'hennessy-vs',
                'name': 'Hennessy V.S',
                'description': 'Французький коньяк. Фрукти, дуб, ваніль.',
                'category': 'cognac',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['classic', 'aged'],
            },
            {
                'slug': 'remy-martin-vsop',
                'name': 'Rémy Martin VSOP',
                'description': 'Преміум коньяк. Квіткові ноти, спеції, шовковистий фініш.',
                'category': 'cognac',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium', 'aged'],
            },
            
            # Лікери
            {
                'slug': 'baileys-original',
                'name': 'Baileys Original',
                'description': 'Ірландський вершковий лікер. Шоколад, ваніль, кава.',
                'category': 'liqueur',
                'strength': 'regular',
                'abv': Decimal('17.0'),
                'tags': ['sweet', 'classic'],
            },
            {
                'slug': 'kahlua',
                'name': 'Kahlúa',
                'description': 'Мексиканський кавовий лікер. Насичений смак кави та ванілі.',
                'category': 'liqueur',
                'strength': 'regular',
                'abv': Decimal('20.0'),
                'tags': ['sweet'],
            },
            {
                'slug': 'cointreau',
                'name': 'Cointreau',
                'description': 'Французький апельсиновий лікер. Цитрусовий, елегантний.',
                'category': 'liqueur',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium', 'fruit'],
            },
            {
                'slug': 'amaretto-disaronno',
                'name': 'Disaronno Amaretto',
                'description': 'Італійський мигдальний лікер. Солодкий, насичений.',
                'category': 'liqueur',
                'strength': 'regular',
                'abv': Decimal('28.0'),
                'tags': ['sweet', 'classic'],
            },
            
            # Вино
            {
                'slug': 'red-dry-wine',
                'name': 'Червоне сухе вино',
                'description': 'Класичне червоне сухе вино. Танінне, фруктове.',
                'category': 'wine',
                'strength': 'regular',
                'abv': Decimal('13.0'),
                'tags': ['classic', 'dry'],
            },
            {
                'slug': 'white-dry-wine',
                'name': 'Біле сухе вино',
                'description': 'Легке біле сухе вино. Цитрусові, мінеральні ноти.',
                'category': 'wine',
                'strength': 'regular',
                'abv': Decimal('12.0'),
                'tags': ['classic', 'dry', 'light'],
            },
            {
                'slug': 'rose-wine',
                'name': 'Рожеве вино',
                'description': 'Освіжаюче рожеве вино. Ягоди, квіти, легка кислинка.',
                'category': 'wine',
                'strength': 'regular',
                'abv': Decimal('12.5'),
                'tags': ['light', 'fruit'],
            },
            
            # Шампанське / Ігристе
            {
                'slug': 'prosecco',
                'name': 'Prosecco',
                'description': 'Італійське ігристе вино. Легке, фруктове, святкове.',
                'category': 'champagne',
                'strength': 'regular',
                'abv': Decimal('11.0'),
                'tags': ['sparkling', 'light', 'fruit'],
            },
            {
                'slug': 'brut-champagne',
                'name': 'Брют шампанське',
                'description': 'Класичне французьке шампанське. Елегантне, сухе.',
                'category': 'champagne',
                'strength': 'regular',
                'abv': Decimal('12.0'),
                'tags': ['sparkling', 'dry', 'premium'],
            },
            
            # Пиво
            {
                'slug': 'lager-beer',
                'name': 'Світле пиво (Лагер)',
                'description': 'Класичне світле пиво. Легке, освіжаюче.',
                'category': 'beer',
                'strength': 'regular',
                'abv': Decimal('5.0'),
                'tags': ['classic', 'light'],
            },
            {
                'slug': 'craft-ipa',
                'name': 'Крафтове IPA',
                'description': 'Крафтове пиво Indian Pale Ale. Хмільне, цитрусове.',
                'category': 'beer',
                'strength': 'regular',
                'abv': Decimal('6.5'),
                'tags': ['craft', 'strong'],
            },
            {
                'slug': 'dark-stout',
                'name': 'Темний стаут',
                'description': 'Темне пиво стаут. Кава, шоколад, карамель.',
                'category': 'beer',
                'strength': 'regular',
                'abv': Decimal('5.5'),
                'tags': ['craft', 'strong'],
            },
            
            # Аперитиви
            {
                'slug': 'aperol',
                'name': 'Aperol',
                'description': 'Італійський аперитив. Гіркуватий, апельсиновий, трав\'яний.',
                'category': 'aperitif',
                'strength': 'regular',
                'abv': Decimal('11.0'),
                'tags': ['classic', 'herbal', 'light'],
            },
            {
                'slug': 'campari',
                'name': 'Campari',
                'description': 'Італійський гіркий аперитив. Інтенсивний, трав\'яний.',
                'category': 'aperitif',
                'strength': 'regular',
                'abv': Decimal('25.0'),
                'tags': ['classic', 'herbal'],
            },
            {
                'slug': 'martini-bianco',
                'name': 'Martini Bianco',
                'description': 'Італійський білий вермут. Солодкий, ванільний, трав\'яний.',
                'category': 'vermouth',
                'strength': 'regular',
                'abv': Decimal('15.0'),
                'tags': ['sweet', 'herbal'],
            },
            
            # Сидр
            {
                'slug': 'apple-cider',
                'name': 'Яблучний сидр',
                'description': 'Класичний яблучний сидр. Освіжаючий, фруктовий.',
                'category': 'cider',
                'strength': 'regular',
                'abv': Decimal('5.0'),
                'tags': ['fruit', 'light'],
            },
            
            # Безалкогольні
            {
                'slug': 'non-alc-beer',
                'name': 'Безалкогольне пиво',
                'description': 'Пиво без алкоголю. Смак пива, але можна за кермом.',
                'category': 'non-alcoholic',
                'strength': 'non_alcoholic',
                'abv': Decimal('0.5'),
                'tags': ['light'],
            },
            {
                'slug': 'non-alc-wine',
                'name': 'Безалкогольне вино',
                'description': 'Вино без алкоголю. Для тих, хто не п\'є.',
                'category': 'non-alcoholic',
                'strength': 'non_alcoholic',
                'abv': Decimal('0.0'),
                'tags': ['light'],
            },
            
            # ========== ДОДАТКОВІ НАПОЇ (40+) ==========
            
            # Горілка - додаткові
            {
                'slug': 'finlandia-vodka',
                'name': 'Finlandia',
                'description': 'Фінська горілка з льодовикової води. Кристально чиста.',
                'category': 'vodka',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium', 'classic'],
            },
            {
                'slug': 'smirnoff-vodka',
                'name': 'Smirnoff',
                'description': 'Класична горілка потрійної дистиляції.',
                'category': 'vodka',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['classic'],
            },
            {
                'slug': 'beluga-vodka',
                'name': 'Beluga Noble',
                'description': 'Російська преміум горілка. Елегантна, шовковиста.',
                'category': 'vodka',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium'],
            },
            {
                'slug': 'khortytsia-vodka',
                'name': 'Хортиця',
                'description': 'Українська горілка. Класичний смак.',
                'category': 'vodka',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['classic', 'budget'],
            },
            
            # Віскі - додаткові
            {
                'slug': 'chivas-regal-12',
                'name': 'Chivas Regal 12',
                'description': 'Шотландський купаж 12 років. М\'який, фруктовий.',
                'category': 'whiskey',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium', 'aged'],
            },
            {
                'slug': 'glenfiddich-12',
                'name': 'Glenfiddich 12',
                'description': 'Односолодовий шотландський. Грушевий, дубовий.',
                'category': 'whiskey',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium', 'aged'],
            },
            {
                'slug': 'tullamore-dew',
                'name': 'Tullamore D.E.W.',
                'description': 'Ірландський потрійної дистиляції. М\'який, солодкуватий.',
                'category': 'whiskey',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['classic'],
            },
            {
                'slug': 'jim-beam',
                'name': 'Jim Beam',
                'description': 'Американський бурбон. Карамель, ваніль, дуб.',
                'category': 'whiskey',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['classic'],
            },
            {
                'slug': 'wild-turkey-101',
                'name': 'Wild Turkey 101',
                'description': 'Міцний бурбон. Насичений, пряний.',
                'category': 'whiskey',
                'strength': 'strong',
                'abv': Decimal('50.5'),
                'tags': ['strong'],
            },
            
            # Ром - додаткові
            {
                'slug': 'malibu-rum',
                'name': 'Malibu',
                'description': 'Кокосовий ром. Солодкий, тропічний.',
                'category': 'rum',
                'strength': 'regular',
                'abv': Decimal('21.0'),
                'tags': ['sweet', 'fruit'],
            },
            {
                'slug': 'kraken-rum',
                'name': 'Kraken Black Spiced',
                'description': 'Темний пряний ром. Насичений, з нотами спецій.',
                'category': 'rum',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['spicy', 'strong'],
            },
            {
                'slug': 'diplomatico-rum',
                'name': 'Diplomático Reserva',
                'description': 'Венесуельський преміум ром. Шоколад, карамель.',
                'category': 'rum',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium', 'aged', 'sweet'],
            },
            
            # Джин - додаткові
            {
                'slug': 'tanqueray-gin',
                'name': 'Tanqueray',
                'description': 'Лондонський сухий джин. Ялівець, кориця.',
                'category': 'gin',
                'strength': 'strong',
                'abv': Decimal('43.1'),
                'tags': ['classic'],
            },
            {
                'slug': 'beefeater-gin',
                'name': 'Beefeater',
                'description': 'Класичний лондонський джин. Цитрус, ялівець.',
                'category': 'gin',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['classic'],
            },
            {
                'slug': 'monkey-47-gin',
                'name': 'Monkey 47',
                'description': 'Німецький крафтовий джин. 47 ботанічних інгредієнтів.',
                'category': 'gin',
                'strength': 'strong',
                'abv': Decimal('47.0'),
                'tags': ['premium', 'craft', 'herbal'],
            },
            
            # Текіла - додаткові
            {
                'slug': 'olmeca-gold',
                'name': 'Olmeca Gold',
                'description': 'Мексиканська золота текіла. М\'яка, з нотами агави.',
                'category': 'tequila',
                'strength': 'strong',
                'abv': Decimal('38.0'),
                'tags': ['classic'],
            },
            {
                'slug': 'don-julio-blanco',
                'name': 'Don Julio Blanco',
                'description': 'Преміум біла текіла. Чиста агава, цитрус.',
                'category': 'tequila',
                'strength': 'strong',
                'abv': Decimal('38.0'),
                'tags': ['premium'],
            },
            {
                'slug': 'espolon-reposado',
                'name': 'Espolón Reposado',
                'description': 'Витримана текіла. Ваніль, карамель, агава.',
                'category': 'tequila',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['aged'],
            },
            
            # Коньяк - додаткові
            {
                'slug': 'courvoisier-vs',
                'name': 'Courvoisier V.S',
                'description': 'Французький коньяк. Квіти, фрукти, ваніль.',
                'category': 'cognac',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['classic'],
            },
            {
                'slug': 'martell-vs',
                'name': 'Martell V.S',
                'description': 'Французький коньяк. Фрукти, дуб, м\'який фініш.',
                'category': 'cognac',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['classic'],
            },
            
            # Лікери - додаткові
            {
                'slug': 'jagermeister',
                'name': 'Jägermeister',
                'description': 'Німецький трав\'яний лікер. 56 трав та спецій.',
                'category': 'liqueur',
                'strength': 'strong',
                'abv': Decimal('35.0'),
                'tags': ['herbal', 'classic'],
            },
            {
                'slug': 'sambuca',
                'name': 'Sambuca',
                'description': 'Італійський анісовий лікер. Солодкий, пряний.',
                'category': 'liqueur',
                'strength': 'strong',
                'abv': Decimal('38.0'),
                'tags': ['sweet', 'herbal'],
            },
            {
                'slug': 'limoncello',
                'name': 'Limoncello',
                'description': 'Італійський лимонний лікер. Яскравий, освіжаючий.',
                'category': 'liqueur',
                'strength': 'regular',
                'abv': Decimal('25.0'),
                'tags': ['sweet', 'fruit'],
            },
            {
                'slug': 'grand-marnier',
                'name': 'Grand Marnier',
                'description': 'Французький апельсиновий лікер на коньяку.',
                'category': 'liqueur',
                'strength': 'strong',
                'abv': Decimal('40.0'),
                'tags': ['premium', 'fruit'],
            },
            {
                'slug': 'blue-curacao',
                'name': 'Blue Curaçao',
                'description': 'Блакитний апельсиновий лікер. Для коктейлів.',
                'category': 'liqueur',
                'strength': 'regular',
                'abv': Decimal('20.0'),
                'tags': ['sweet', 'fruit'],
            },
            {
                'slug': 'midori-melon',
                'name': 'Midori',
                'description': 'Японський динний лікер. Солодкий, яскраво-зелений.',
                'category': 'liqueur',
                'strength': 'regular',
                'abv': Decimal('20.0'),
                'tags': ['sweet', 'fruit'],
            },
            
            # Вино - додаткові
            {
                'slug': 'cabernet-sauvignon',
                'name': 'Каберне Совіньйон',
                'description': 'Повнотіле червоне вино. Чорна смородина, дуб.',
                'category': 'wine',
                'strength': 'regular',
                'abv': Decimal('13.5'),
                'tags': ['classic', 'dry'],
            },
            {
                'slug': 'merlot-wine',
                'name': 'Мерло',
                'description': 'М\'яке червоне вино. Слива, вишня, шоколад.',
                'category': 'wine',
                'strength': 'regular',
                'abv': Decimal('13.0'),
                'tags': ['classic', 'dry'],
            },
            {
                'slug': 'pinot-noir',
                'name': 'Піно Нуар',
                'description': 'Елегантне червоне вино. Вишня, малина, спеції.',
                'category': 'wine',
                'strength': 'regular',
                'abv': Decimal('13.0'),
                'tags': ['premium', 'light'],
            },
            {
                'slug': 'chardonnay',
                'name': 'Шардоне',
                'description': 'Біле вино. Яблуко, ваніль, масляні ноти.',
                'category': 'wine',
                'strength': 'regular',
                'abv': Decimal('13.0'),
                'tags': ['classic', 'dry'],
            },
            {
                'slug': 'sauvignon-blanc',
                'name': 'Совіньйон Блан',
                'description': 'Свіже біле вино. Цитрус, трави, мінеральність.',
                'category': 'wine',
                'strength': 'regular',
                'abv': Decimal('12.5'),
                'tags': ['classic', 'dry', 'light'],
            },
            {
                'slug': 'riesling-wine',
                'name': 'Рислінг',
                'description': 'Ароматне біле вино. Персик, мед, квіти.',
                'category': 'wine',
                'strength': 'regular',
                'abv': Decimal('11.0'),
                'tags': ['sweet', 'fruit', 'light'],
            },
            {
                'slug': 'moscato-wine',
                'name': 'Москато',
                'description': 'Солодке ігристе вино. Персик, абрикос, мед.',
                'category': 'wine',
                'strength': 'regular',
                'abv': Decimal('5.5'),
                'tags': ['sweet', 'sparkling', 'light'],
            },
            
            # Шампанське - додаткові
            {
                'slug': 'moet-chandon',
                'name': 'Moët & Chandon',
                'description': 'Преміум французьке шампанське. Елегантне, святкове.',
                'category': 'champagne',
                'strength': 'regular',
                'abv': Decimal('12.0'),
                'tags': ['premium', 'sparkling'],
            },
            {
                'slug': 'veuve-clicquot',
                'name': 'Veuve Clicquot',
                'description': 'Знамените шампанське. Фрукти, бриош.',
                'category': 'champagne',
                'strength': 'regular',
                'abv': Decimal('12.0'),
                'tags': ['premium', 'sparkling'],
            },
            {
                'slug': 'asti-spumante',
                'name': 'Asti Spumante',
                'description': 'Італійське солодке ігристе. Мускат, персик.',
                'category': 'champagne',
                'strength': 'regular',
                'abv': Decimal('7.0'),
                'tags': ['sweet', 'sparkling', 'light'],
            },
            {
                'slug': 'cava-brut',
                'name': 'Cava Brut',
                'description': 'Іспанське ігристе вино. Свіже, цитрусове.',
                'category': 'champagne',
                'strength': 'regular',
                'abv': Decimal('11.5'),
                'tags': ['sparkling', 'dry'],
            },
            
            # Пиво - додаткові
            {
                'slug': 'wheat-beer',
                'name': 'Пшеничне пиво',
                'description': 'Німецьке Weizen. Банан, гвоздика, освіжаюче.',
                'category': 'beer',
                'strength': 'regular',
                'abv': Decimal('5.0'),
                'tags': ['craft', 'light'],
            },
            {
                'slug': 'porter-beer',
                'name': 'Портер',
                'description': 'Темне пиво. Кава, шоколад, карамель.',
                'category': 'beer',
                'strength': 'regular',
                'abv': Decimal('5.5'),
                'tags': ['craft'],
            },
            {
                'slug': 'pilsner-beer',
                'name': 'Пілснер',
                'description': 'Чеське світле пиво. Хміль, солод, свіжість.',
                'category': 'beer',
                'strength': 'regular',
                'abv': Decimal('4.5'),
                'tags': ['classic', 'light'],
            },
            {
                'slug': 'belgian-ale',
                'name': 'Бельгійський ель',
                'description': 'Крафтове бельгійське пиво. Фрукти, спеції.',
                'category': 'beer',
                'strength': 'regular',
                'abv': Decimal('7.0'),
                'tags': ['craft', 'premium'],
            },
            
            # Аперитиви - додаткові
            {
                'slug': 'pimms',
                'name': 'Pimm\'s No. 1',
                'description': 'Британський аперитив. Трави, цитрус, огірок.',
                'category': 'aperitif',
                'strength': 'regular',
                'abv': Decimal('25.0'),
                'tags': ['classic', 'herbal'],
            },
            {
                'slug': 'lillet-blanc',
                'name': 'Lillet Blanc',
                'description': 'Французький аперитив. Апельсин, мед, квіти.',
                'category': 'aperitif',
                'strength': 'regular',
                'abv': Decimal('17.0'),
                'tags': ['premium', 'fruit'],
            },
            
            # Вермут - додаткові
            {
                'slug': 'martini-rosso',
                'name': 'Martini Rosso',
                'description': 'Червоний солодкий вермут. Трави, карамель.',
                'category': 'vermouth',
                'strength': 'regular',
                'abv': Decimal('15.0'),
                'tags': ['sweet', 'herbal', 'classic'],
            },
            {
                'slug': 'martini-dry',
                'name': 'Martini Extra Dry',
                'description': 'Сухий вермут. Легкий, цитрусовий.',
                'category': 'vermouth',
                'strength': 'regular',
                'abv': Decimal('15.0'),
                'tags': ['dry', 'herbal'],
            },
            {
                'slug': 'cinzano-rosso',
                'name': 'Cinzano Rosso',
                'description': 'Італійський червоний вермут. Гірко-солодкий.',
                'category': 'vermouth',
                'strength': 'regular',
                'abv': Decimal('14.4'),
                'tags': ['sweet', 'herbal'],
            },
            
            # Сидр - додаткові
            {
                'slug': 'pear-cider',
                'name': 'Грушевий сидр',
                'description': 'Сидр з груш. Солодкий, освіжаючий.',
                'category': 'cider',
                'strength': 'regular',
                'abv': Decimal('4.5'),
                'tags': ['fruit', 'sweet', 'light'],
            },
            {
                'slug': 'cherry-cider',
                'name': 'Вишневий сидр',
                'description': 'Сидр з вишнею. Кисло-солодкий, ягідний.',
                'category': 'cider',
                'strength': 'regular',
                'abv': Decimal('4.0'),
                'tags': ['fruit', 'light'],
            },
            
            # Безалкогольні - додаткові
            {
                'slug': 'non-alc-prosecco',
                'name': 'Безалкогольне просеко',
                'description': 'Ігристе без алкоголю. Святкове, освіжаюче.',
                'category': 'non-alcoholic',
                'strength': 'non_alcoholic',
                'abv': Decimal('0.0'),
                'tags': ['sparkling', 'light'],
            },
            {
                'slug': 'kombucha',
                'name': 'Комбуча',
                'description': 'Ферментований чай. Освіжаючий, корисний.',
                'category': 'non-alcoholic',
                'strength': 'non_alcoholic',
                'abv': Decimal('0.5'),
                'tags': ['craft', 'herbal'],
            },
        ]
        
        created = 0
        for drink_data in drinks_data:
            drink, was_created = Drink.objects.get_or_create(
                slug=drink_data['slug'],
                defaults={
                    'name': drink_data['name'],
                    'description': drink_data['description'],
                    'category': categories.get(drink_data['category']),
                    'strength': drink_data['strength'],
                    'abv': drink_data['abv'],
                }
            )
            
            # Додаємо теги
            if drink_data.get('tags'):
                for tag_slug in drink_data['tags']:
                    if tag_slug in tags:
                        drink.tags.add(tags[tag_slug])
            
            if was_created:
                created += 1
        
        self.stdout.write(f'  ✓ Напоїв: {len(drinks_data)} (нових: {created})')

    def link_drinks_to_scenarios(self):
        """Прив'язуємо напої до сценаріїв як рекомендовані."""
        from events.models import Scenario, Drink
        
        # Маппінг сценаріїв на рекомендовані напої
        scenario_drinks = {
            'romantic-dinner': [
                'red-dry-wine', 'white-dry-wine', 'rose-wine', 'prosecco', 'brut-champagne',
                'cabernet-sauvignon', 'merlot-wine', 'pinot-noir', 'chardonnay', 'sauvignon-blanc',
                'moet-chandon', 'veuve-clicquot', 'moscato-wine',
            ],
            'football-night': [
                'lager-beer', 'craft-ipa', 'dark-stout', 'pilsner-beer', 'wheat-beer',
                'jack-daniels', 'jim-beam', 'absolut-vodka', 'smirnoff-vodka',
            ],
            'house-party': [
                'absolut-vodka', 'grey-goose', 'nemiroff-honey-pepper', 'smirnoff-vodka',
                'jack-daniels', 'jameson', 'bacardi-white', 'captain-morgan-spiced',
                'prosecco', 'lager-beer', 'craft-ipa',
                'jagermeister', 'baileys-original', 'aperol', 'campari',
            ],
            'budget-evening': [
                'lager-beer', 'pilsner-beer', 'khortytsia-vodka', 'smirnoff-vodka',
                'apple-cider', 'red-dry-wine', 'white-dry-wine',
            ],
            'friends-gathering': [
                'jack-daniels', 'jameson', 'makers-mark', 'craft-ipa', 'dark-stout', 'wheat-beer',
                'cabernet-sauvignon', 'merlot-wine', 'aperol', 'campari',
                'absolut-vodka', 'grey-goose', 'gordon-gin', 'bombay-sapphire',
            ],
            'first-date': [
                'white-dry-wine', 'rose-wine', 'prosecco', 'brut-champagne',
                'chardonnay', 'sauvignon-blanc', 'pinot-noir',
                'aperol', 'martini-bianco', 'lillet-blanc',
            ],
        }
        
        linked = 0
        for scenario_slug, drink_slugs in scenario_drinks.items():
            try:
                scenario = Scenario.objects.get(slug=scenario_slug)
                drinks = Drink.objects.filter(slug__in=drink_slugs)
                scenario.drinks.add(*drinks)
                linked += drinks.count()
            except Scenario.DoesNotExist:
                self.stdout.write(f'  ⚠️ Сценарій {scenario_slug} не знайдено')
        
        self.stdout.write(f'  ✓ Прив\'язано напоїв до сценаріїв: {linked}')
