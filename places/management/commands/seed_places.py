"""
Скрипт для заповнення бази даних тестовими місцями у Києві.
Запуск: python manage.py seed_places
"""
from django.core.management.base import BaseCommand
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Заповнює базу даних тестовими місцями у Києві (бари, магазини, акції)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Починаємо заповнення місцями...'))
        
        self.create_places()
        self.create_promotions()
        
        self.stdout.write(self.style.SUCCESS('✅ Місця успішно створено!'))

    def create_places(self):
        """Створюємо місця у Києві."""
        from places.models import Place
        
        places_data = [
            # ==================== БАРИ ====================
            {
                'name': 'Барман Диктат',
                'kind': 'bar',
                'lat': 50.4501,
                'lon': 30.5234,
                'city': 'Київ',
                'address': 'вул. Хрещатик, 15',
                'url': 'https://instagram.com/barman_diktatur',
            },
            {
                'name': 'Parovoz Speak Easy',
                'kind': 'bar',
                'lat': 50.4488,
                'lon': 30.5198,
                'city': 'Київ',
                'address': 'вул. Пушкінська, 11',
                'url': 'https://parovoz.bar',
            },
            {
                'name': 'Loggerhead',
                'kind': 'bar',
                'lat': 50.4412,
                'lon': 30.5187,
                'city': 'Київ',
                'address': 'вул. Саксаганського, 41',
                'url': 'https://loggerhead.bar',
            },
            {
                'name': 'Pink Freud',
                'kind': 'bar',
                'lat': 50.4467,
                'lon': 30.5112,
                'city': 'Київ',
                'address': 'вул. Шота Руставелі, 16',
                'url': 'https://pinkfreud.bar',
            },
            {
                'name': 'Підвал',
                'kind': 'bar',
                'lat': 50.4521,
                'lon': 30.5156,
                'city': 'Київ',
                'address': 'вул. Прорізна, 8',
                'url': '',
            },
            {
                'name': 'Palata №6',
                'kind': 'bar',
                'lat': 50.4389,
                'lon': 30.5201,
                'city': 'Київ',
                'address': 'вул. Жилянська, 75',
                'url': 'https://palata6.kyiv.ua',
            },
            {
                'name': 'Bzbee Wine Bar',
                'kind': 'bar',
                'lat': 50.4534,
                'lon': 30.5189,
                'city': 'Київ',
                'address': 'вул. Золотоворітська, 2',
                'url': 'https://bzbee.wine',
            },
            {
                'name': 'Alchemist Bar',
                'kind': 'bar',
                'lat': 50.4445,
                'lon': 30.5098,
                'city': 'Київ',
                'address': 'вул. Антоновича, 52',
                'url': 'https://alchemist.bar',
            },
            # ==================== МАГАЗИНИ ====================
            {
                'name': 'Good Wine',
                'kind': 'shop',
                'lat': 50.4312,
                'lon': 30.5234,
                'city': 'Київ',
                'address': 'вул. Мечникова, 9',
                'url': 'https://goodwine.ua',
            },
            {
                'name': 'Виноград',
                'kind': 'shop',
                'lat': 50.4478,
                'lon': 30.5145,
                'city': 'Київ',
                'address': 'вул. Басейна, 1/2',
                'url': 'https://vinograd.com.ua',
            },
            {
                'name': 'Wine Time',
                'kind': 'shop',
                'lat': 50.4401,
                'lon': 30.5289,
                'city': 'Київ',
                'address': 'вул. Велика Васильківська, 72',
                'url': 'https://winetime.com.ua',
            },
            {
                'name': 'Сільпо Гурме',
                'kind': 'shop',
                'lat': 50.4356,
                'lon': 30.5167,
                'city': 'Київ',
                'address': 'вул. Льва Толстого, 57',
                'url': 'https://silpo.ua',
            },
            {
                'name': 'Le Silpo',
                'kind': 'shop',
                'lat': 50.4489,
                'lon': 30.5212,
                'city': 'Київ',
                'address': 'вул. Хрещатик, 44',
                'url': 'https://lesilpo.ua',
            },
            {
                'name': 'Craft Beer Store',
                'kind': 'shop',
                'lat': 50.4523,
                'lon': 30.5078,
                'city': 'Київ',
                'address': 'вул. Ярославів Вал, 21',
                'url': 'https://craftbeer.ua',
            },
            {
                'name': 'Whisky Corner',
                'kind': 'shop',
                'lat': 50.4398,
                'lon': 30.5156,
                'city': 'Київ',
                'address': 'вул. Саксаганського, 119',
                'url': 'https://whiskycorner.com.ua',
            },
            {
                'name': 'Wine Bureau',
                'kind': 'shop',
                'lat': 50.4445,
                'lon': 30.5234,
                'city': 'Київ',
                'address': 'вул. Городецького, 4',
                'url': 'https://winebureau.ua',
            },
            # ==================== ІНШІ ====================
            {
                'name': 'Коктейльна Академія',
                'kind': 'other',
                'lat': 50.4512,
                'lon': 30.5123,
                'city': 'Київ',
                'address': 'вул. Володимирська, 67',
                'url': 'https://cocktail-academy.ua',
            },
            {
                'name': 'Bartender School Kyiv',
                'kind': 'other',
                'lat': 50.4367,
                'lon': 30.5198,
                'city': 'Київ',
                'address': 'вул. Жилянська, 48',
                'url': 'https://bartenderschool.ua',
            },
            {
                'name': 'Wine Club Kyiv',
                'kind': 'other',
                'lat': 50.4456,
                'lon': 30.5167,
                'city': 'Київ',
                'address': 'вул. Пушкінська, 31',
                'url': 'https://wineclub.kyiv.ua',
            },
        ]
        
        created = 0
        for place_data in places_data:
            place, was_created = Place.objects.get_or_create(
                name=place_data['name'],
                defaults=place_data
            )
            if was_created:
                created += 1
        
        self.stdout.write(f'  ✓ Місць: {len(places_data)} (нових: {created})')

    def create_promotions(self):
        """Створюємо акції для місць."""
        from places.models import Place, Promotion
        
        today = date.today()
        
        promotions_data = [
            # Бари
            {
                'place_name': 'Барман Диктат',
                'title': 'Happy Hour: -30% на коктейлі',
                'description': 'Щодня з 17:00 до 20:00 знижка 30% на всі авторські коктейлі. Не пропустіть!',
                'valid_from': today,
                'valid_to': today + timedelta(days=60),
            },
            {
                'place_name': 'Parovoz Speak Easy',
                'title': '2 коктейлі за ціною 1',
                'description': 'Акція "Друг бармена" - приведи друга та отримай другий коктейль безкоштовно.',
                'valid_from': today,
                'valid_to': today + timedelta(days=30),
            },
            {
                'place_name': 'Loggerhead',
                'title': 'Craft Beer Week',
                'description': 'Тиждень крафтового пива! Спеціальні ціни на понад 20 сортів крафту.',
                'valid_from': today,
                'valid_to': today + timedelta(days=7),
            },
            {
                'place_name': 'Pink Freud',
                'title': 'DJ Night -20%',
                'description': 'Кожної п\'ятниці та суботи знижка 20% на весь бар під час DJ-сетів.',
                'valid_from': today,
                'valid_to': today + timedelta(days=90),
            },
            {
                'place_name': 'Підвал',
                'title': 'Shot Night',
                'description': 'Середа - день шотів! Всі шоти по 49 грн.',
                'valid_from': today,
                'valid_to': today + timedelta(days=60),
            },
            {
                'place_name': 'Palata №6',
                'title': 'Безкоштовний вхід',
                'description': 'Для всіх гостей до 22:00 - безкоштовний вхід та welcome drink.',
                'valid_from': today,
                'valid_to': today + timedelta(days=45),
            },
            {
                'place_name': 'Bzbee Wine Bar',
                'title': 'Wine Tasting: 5 вин за 350 грн',
                'description': 'Щочетверга дегустаційний сет з 5 вин від сомельє за спеціальною ціною.',
                'valid_from': today,
                'valid_to': today + timedelta(days=30),
            },
            {
                'place_name': 'Alchemist Bar',
                'title': 'Коктейль дня: -40%',
                'description': 'Щодня новий коктейль дня зі знижкою 40%. Запитуйте у бармена!',
                'valid_from': today,
                'valid_to': today + timedelta(days=90),
            },
            # Магазини
            {
                'place_name': 'Good Wine',
                'title': '-15% на італійські вина',
                'description': 'Знижка 15% на всю колекцію вин з Італії. Barolo, Chianti, Prosecco та інші.',
                'valid_from': today,
                'valid_to': today + timedelta(days=14),
            },
            {
                'place_name': 'Виноград',
                'title': '3 пляшки = -20%',
                'description': 'При купівлі 3 та більше пляшок вина - знижка 20% на всю покупку.',
                'valid_from': today,
                'valid_to': today + timedelta(days=30),
            },
            {
                'place_name': 'Wine Time',
                'title': 'Безкоштовна доставка',
                'description': 'Безкоштовна доставка по Києву при замовленні від 1000 грн.',
                'valid_from': today,
                'valid_to': today + timedelta(days=60),
            },
            {
                'place_name': 'Сільпо Гурме',
                'title': 'Тиждень віскі',
                'description': 'Знижки до 25% на преміальний віскі. Glenfiddich, Macallan, Jameson.',
                'valid_from': today,
                'valid_to': today + timedelta(days=7),
            },
            {
                'place_name': 'Le Silpo',
                'title': 'Дегустація шампанського',
                'description': 'Щосуботи з 15:00 до 19:00 безкоштовна дегустація шампанського та ігристих вин.',
                'valid_from': today,
                'valid_to': today + timedelta(days=30),
            },
            {
                'place_name': 'Craft Beer Store',
                'title': 'Новинки крафту -10%',
                'description': 'Знижка 10% на всі новинки місяця. Оновлення щотижня!',
                'valid_from': today,
                'valid_to': today + timedelta(days=30),
            },
            {
                'place_name': 'Whisky Corner',
                'title': 'Клубна картка: бонуси',
                'description': 'Отримуйте 5% бонусів на картку з кожної покупки. Діє накопичення.',
                'valid_from': today,
                'valid_to': today + timedelta(days=365),
            },
            {
                'place_name': 'Wine Bureau',
                'title': 'Персональний сомельє',
                'description': 'Безкоштовна консультація сомельє при покупці від 2000 грн.',
                'valid_from': today,
                'valid_to': today + timedelta(days=90),
            },
            # Інші
            {
                'place_name': 'Коктейльна Академія',
                'title': 'Майстер-клас для двох',
                'description': 'Романтичний майстер-клас з приготування коктейлів для пари. 1500 грн.',
                'valid_from': today,
                'valid_to': today + timedelta(days=60),
            },
            {
                'place_name': 'Bartender School Kyiv',
                'title': 'Перший урок безкоштовно',
                'description': 'Пробний урок бартендерства безкоштовно. Запишіться на сайті!',
                'valid_from': today,
                'valid_to': today + timedelta(days=90),
            },
            {
                'place_name': 'Wine Club Kyiv',
                'title': 'Членство зі знижкою 50%',
                'description': 'Перший місяць членства у Wine Club зі знижкою 50%. Дегустації, лекції, знижки.',
                'valid_from': today,
                'valid_to': today + timedelta(days=30),
            },
        ]
        
        created = 0
        for promo_data in promotions_data:
            place_name = promo_data.pop('place_name')
            try:
                place = Place.objects.get(name=place_name)
                promo, was_created = Promotion.objects.get_or_create(
                    place=place,
                    title=promo_data['title'],
                    defaults=promo_data
                )
                if was_created:
                    created += 1
            except Place.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Місце не знайдено: {place_name}')
                )
        
        self.stdout.write(f'  ✓ Акцій: {len(promotions_data)} (нових: {created})')
