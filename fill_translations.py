#!/usr/bin/env python
"""
Скрипт для заповнення перекладів у PO файлі.
Заповнює порожні msgstr англійськими перекладами.
"""

# Словник українсько-англійських перекладів
TRANSLATIONS = {
    # Settings & Language
    "email address": "email address",
    "English": "English",
    "Українська": "Ukrainian",
    "Російська": "Russian",
    
    # Forms
    "Будь-яка": "Any",
    "Назва місця, напр. Бар Шухляда": "Place name, e.g. Bar Shukhlyada",
    "Адреса, напр. вул. Хрещатик 1": "Address, e.g. 1 Khreshchatyk St.",
    "Назва місця": "Place name",
    "Адреса": "Address",
    
    # Difficulty
    "Дуже просто": "Very easy",
    "Середньо": "Medium",
    "Складніше": "Harder",
    "Складність страви": "Dish difficulty",
    
    # Quiz
    "Вгадай коктейль": "Guess the cocktail",
    "Вгадай назву коктейлю за інгредієнтами та отримай бали!": "Guess the cocktail name by ingredients and earn points!",
    "Бали": "Points",
    "Серія": "Streak",
    "Відповідей": "Answers",
    "Завантаження питання...": "Loading question...",
    "Які інгредієнти?": "What ingredients?",
    "Правильно!": "Correct!",
    "Наступне питання": "Next question",
    "Помилка завантаження": "Loading error",
    "Це був": "It was",
    "Неправильно": "Wrong",
    "Правильна відповідь:": "Correct answer:",
    
    # Events
    "Активні": "Active",
    "Архів": "Archive",
    "Архів подій": "Events archive",
    "Учасник": "Participant",
    "год": "h",
    "чел.": "ppl",
    "Локація уточнюється": "Location TBD",
    "Детальніше": "Details",
    "Покупки": "Shopping",
    "Обрати сценарій": "Choose scenario",
    "Подій поки немає": "No events yet",
    "почни з": "start with",
    "і створи першу.": "and create your first one.",
    "Слідкуй за подіями, місцем і часом на одному екрані.": "Track events, location and time on one screen.",
    
    # Profile menu
    "Друзі": "Friends",
    "Знайти друзів, запити": "Find friends, requests",
    "Статистика": "Statistics",
    "Графіки та звіти": "Charts and reports",
    "Досягнення": "Achievements",
    "Ачивки та нагороди": "Badges and rewards",
    "Щоденні завдання": "Daily tasks",
    
    # Dashboard
    "Коктейльна вікторина": "Cocktail quiz",
    "Перевір свої знання": "Test your knowledge",
    "Пошук за інгредієнтами": "Search by ingredients",
    "Знайди коктейль": "Find a cocktail",
    "Рекомендації": "Recommendations",
    "AI-Сомельє": "AI Sommelier",
    "Персональні рекомендації": "Personal recommendations",
    "BAC Калькулятор": "BAC Calculator",
    "Розрахунок рівня алкоголю": "Blood alcohol calculation",
    "Списки покупок": "Shopping lists",
    "Керуйте покупками": "Manage shopping",
    "Розблокуйте всі функції": "Unlock all features",
    
    # Leaderboard & Gamification
    "Таблиця лідерів": "Leaderboard",
    "Топ користувачів за балами": "Top users by points",
    "Усі учасники": "All participants",
    "Лідерборд": "Leaderboard",
    "Мої досягнення": "My achievements",
    "Вікторина": "Quiz",
    
    # Shopping
    "Мої списки": "My lists",
    "Новий список": "New list",
    "Видалити список": "Delete list",
    "Попередній перегляд": "Preview",
    "Додати до списку": "Add to list",
    
    # Stats
    "Експорт PDF": "Export PDF",
    "Загальна статистика": "General statistics",
    "Подій всього": "Total events",
    "Середній рейтинг": "Average rating",
    
    # Social
    "Список друзів": "Friends list",
    "Запити в друзі": "Friend requests",
    "Додати друга": "Add friend",
    "Прийняти": "Accept",
    "Відхилити": "Decline",
    "Видалити з друзів": "Remove friend",
    
    # Common
    "Назад": "Back",
    "Далі": "Next",
    "Зберегти": "Save",
    "Скасувати": "Cancel",
    "Видалити": "Delete",
    "Редагувати": "Edit",
    "Завантаження...": "Loading...",
    "Помилка": "Error",
    "Успіх": "Success",
    "Попередження": "Warning",
    "Інформація": "Info",
    "Так": "Yes",
    "Ні": "No",
    "Готово": "Done",
    "Закрити": "Close",
    "Пошук": "Search",
    "Фільтр": "Filter",
    "Сортування": "Sort",
    "Всі": "All",
    "Немає даних": "No data",
    
    # Notifications
    "Нові сповіщення": "New notifications",
    "Прочитати все": "Mark all read",
    "Сповіщень немає": "No notifications",
    
    # Premium
    "Premium": "Premium",
    "Преміум": "Premium",
    "Спробувати безкоштовно": "Try for free",
    "Купити Premium": "Buy Premium",
    
    # Diary
    "Щоденник": "Diary",
    "Алко-щоденник": "Alcohol diary",
    "Додати запис": "Add entry",
    "Мої записи": "My entries",
    
    # Places/Map
    "Карта": "Map",
    "Місця": "Places",
    "Знайти на карті": "Find on map",
    
    # Cocktails
    "Коктейлі": "Cocktails",
    "Інгредієнти": "Ingredients",
    "Рецепт": "Recipe",
    "Оцінка": "Rating",
    "Відгуки": "Reviews",
    "Залишити відгук": "Leave review",
    
    # Scenarios
    "Сценарії": "Scenarios",
    "Обрати": "Choose",
    "Улюблені": "Favorites",
    "Категорія": "Category",
    
    # Event details
    "Деталі події": "Event details",
    "Дата": "Date",
    "Час": "Time",
    "Місце": "Place",
    "Кількість гостей": "Number of guests",
    "Тривалість": "Duration",
    "Нотатки": "Notes",
    "Учасники": "Participants",
    "Обговорення": "Discussion",
    "Завершити подію": "Finish event",
    "Редагувати подію": "Edit event",
    "Видалити подію": "Delete event",
    "Запросити друга": "Invite friend",
    
    # AI Sommelier
    "Персональні рекомендації напоїв": "Personal drink recommendations",
    "Отримати рекомендацію": "Get recommendation",
    "На основі ваших уподобань": "Based on your preferences",
    "Оберіть сценарій": "Choose scenario",
    "Оберіть настрій": "Choose mood",
    "Легкий": "Light",
    "Звичайний": "Regular",
    "Міцний": "Strong",
    
    # Mood
    "Настрій": "Mood",
    "Романтичний": "Romantic",
    "Веселий": "Cheerful",
    "Спокійний": "Calm",
    "Енергійний": "Energetic",
    
    # User profile
    "Особисті дані": "Personal data",
    "Змінити пароль": "Change password",
    "Вийти": "Log out",
    "Видалити акаунт": "Delete account",
    "Налаштування": "Settings",
    "Мова": "Language",
    "Тема": "Theme",
    "Темна": "Dark",
    "Світла": "Light",
    
    # Misc new strings
    "Оберіть інгредієнти": "Select ingredients",
    "Оберіть принаймні один інгредієнт": "Select at least one ingredient",
    "Знайдено коктейлів": "Cocktails found",
    "Не знайдено коктейлів з такими інгредієнтами": "No cocktails found with these ingredients",
    "Пошук коктейлів": "Search cocktails",
    "Введіть назву": "Enter name",
    "Без алкоголю": "Non-alcoholic",
    "З алкоголем": "Alcoholic",
    "Мінімальний рейтинг": "Minimum rating",
    
    # Event status
    "Очікує підтвердження": "Pending",
    "Підтверджено": "Confirmed",
    "Завершено": "Completed",
    "Скасовано": "Cancelled",
    
    # More event strings
    "Створити подію": "Create event",
    "Мої події": "My events",
    "Майбутні події": "Upcoming events",
    "Минулі події": "Past events",
    
    # Calculator
    "Розрахувати": "Calculate",
    "Результат": "Result",
    "Вага": "Weight",
    "Стать": "Gender",
    "Чоловік": "Male",
    "Жінка": "Female",
    "Об'єм": "Volume",
    "Міцність": "Strength",
    "Час": "Time",
    "годин": "hours",
    "хвилин": "minutes",
    
    # Registration
    "Реєстрація": "Registration",
    "Увійти": "Sign in",
    "Вийти з акаунту": "Sign out",
    "Email": "Email",
    "Пароль": "Password",
    "Повторіть пароль": "Confirm password",
    "Забули пароль?": "Forgot password?",
    "Запам'ятати мене": "Remember me",
    "Зареєструватися": "Sign up",
    
    # Privacy
    "Політика конфіденційності": "Privacy Policy",
    "Умови використання": "Terms of Service",
    "Погоджуюсь з умовами": "I agree to terms",
    
    # Error messages
    "Щось пішло не так": "Something went wrong",
    "Спробуйте ще раз": "Try again",
    "Сторінку не знайдено": "Page not found",
    "Доступ заборонено": "Access denied",
    
    # Success messages
    "Збережено успішно": "Saved successfully",
    "Видалено успішно": "Deleted successfully",
    "Надіслано успішно": "Sent successfully",
}

def fill_translations(input_path, output_path=None):
    """
    Читає PO файл та заповнює порожні переклади.
    """
    if output_path is None:
        output_path = input_path
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        result.append(line)
        
        # Якщо це msgid, перевіряємо чи наступний msgstr порожній
        if line.startswith('msgid "') and not line.startswith('msgid ""'):
            msgid = line[7:-1]  # Витягуємо текст між msgid " і "
            
            # Перевіряємо чи наступний рядок - msgstr
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line == 'msgstr ""':
                    # Шукаємо переклад
                    if msgid in TRANSLATIONS:
                        result.append(f'msgstr "{TRANSLATIONS[msgid]}"')
                        i += 2
                        continue
        
        # Видаляємо fuzzy якщо є переклад
        if line.startswith('#, fuzzy'):
            # Шукаємо msgid далі
            for j in range(i+1, min(i+5, len(lines))):
                if lines[j].startswith('msgid "') and not lines[j].startswith('msgid ""'):
                    msgid = lines[j][7:-1]
                    if msgid in TRANSLATIONS:
                        # Пропускаємо fuzzy коментар
                        i += 1
                        continue
                    break
        
        i += 1
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))
    
    print(f"Translations filled. Output: {output_path}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        fill_translations(sys.argv[1])
    else:
        fill_translations('/app/locale/en/LC_MESSAGES/django.po')
