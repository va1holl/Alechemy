# Alechemy — Повна документація проєкту

## 1. Загальний опис

**Alechemy** — це веб-застосунок для планування алкогольних подій, побудований на Django. Платформа дозволяє:

- Створювати події за готовими сценаріями (вечірка, побачення, спорт тощо)
- Підбирати напої, страви та коктейлі
- Запрошувати друзів та спільно обговорювати події
- Вести алко-щоденник з розрахунком BAC (рівень алкоголю в крові)
- Отримувати персональні рекомендації щодо випивки, закуски та відновлення
- Формувати списки покупок з автоматичним розрахунком кількості
- Переглядати бари та магазини на карті Києва
- Грати в коктейльну вікторину та заробляти бали
- Слідкувати за статистикою та досягненнями
- Генерувати PDF-звіти (Premium)

---

## 2. Технології та стек

| Компонент | Технологія | Версія |
|---|---|---|
| **Backend** | Django | 5.2.7 |
| **Мова** | Python | 3.12 |
| **База даних** | PostgreSQL | 16 |
| **Кешування** | Redis | 5.0+ |
| **WSGI-сервер (prod)** | Gunicorn | 21.0+ |
| **Reverse proxy (prod)** | Nginx | 1.25-alpine |
| **Контейнеризація** | Docker + Docker Compose | — |
| **REST API** | Django REST Framework | 3.14+ |
| **JWT автентифікація** | djangorestframework-simplejwt | 5.3+ |
| **Хешування паролів** | Argon2 (argon2-cffi) | 23.0+ |
| **PDF-звіти** | ReportLab | 4.0+ |
| **2FA для адмінки** | django-otp | 1.3+ |
| **CAPTCHA** | django-hcaptcha | 0.2+ |
| **Обробка зображень** | Pillow | 10.0+ |
| **Моніторинг помилок** | Sentry SDK | 2.0+ |
| **Email** | Django SMTP (Gmail) | — |

---

## 3. Архітектура проєкту

### 3.1. Структура додатків (Django apps)

```
alechemy/          — Конфігурація проєкту (settings, urls, middleware, wsgi/asgi)
accounts/          — Кастомна автентифікація, профіль, друзі, сповіщення
events/            — Сценарії, події, учасники, алко-щоденник, обговорення
recipes/           — Коктейлі, інгредієнти, рецепти, AI Сомельє
gamification/      — Бали, досягнення, челенджі, вікторина, таблиця лідерів
shopping/          — Калькулятор списку покупок
social/            — Пошук друзів, запити дружби, профілі, лідерборд друзів
places/            — Карта барів та магазинів з акціями
pages/             — Сторінки UI: дашборд, профіль, персональні дані, налаштування, Premium
stats/             — Статистика користувача, експорт PDF
health/            — Health-check endpoint (/health/healthz/)
```

### 3.2. Кількість URL-маршрутів

**95+ маршрутів** у 12 додатках.

### 3.3. Docker

**Development:**
```yaml
services:
  web:
    build: .                    # Dockerfile (python:3.12-slim)
    entrypoint: docker-entrypoint.dev.sh  # migrate + runserver
    ports: 8000:8000
    volumes: .:/app             # live-reload
  db:
    image: postgres:16
    healthcheck: pg_isready
```

**Production:**
```yaml
services:
  web:
    build: Dockerfile.prod      # Multi-stage, non-root user (appuser:appgroup)
    restart: unless-stopped
  db:
    image: postgres:16
  redis:
    image: redis:7-alpine
  nginx:
    image: nginx:1.25-alpine
    ports: 80:80, 443:443
    # Rate limiting, SSL, gzip, static/media serving
```

Production Dockerfile використовує multi-stage build: перший stage створює wheels, другий — фінальний образ з non-root користувачем для безпеки.

---

## 4. Моделі даних

### 4.1. accounts — Автентифікація та профіль

#### User (AbstractUser)
Кастомна модель користувача з email-based автентифікацією.

| Поле | Тип | Опис |
|---|---|---|
| `email` | EmailField (unique) | Основний ідентифікатор для логіну |
| `is_verified` | BooleanField | Чи верифікований email |
| `username` | CharField | Автогенерується з email при реєстрації |

#### Profile (OneToOne → User)
Розширений профіль користувача.

| Поле | Тип | Опис |
|---|---|---|
| `unique_tag` | CharField | Унікальний тег (#ABC123) для пошуку друзів |
| `display_name` | CharField | Публічне ім'я у коментарях та чатах |
| `birth_date` | DateField | Дата народження (замість числового `age`) |
| `age` | @property | Автоматично розраховується з `birth_date` |
| `sex` | CharField (m/f/other) | Стать — для розрахунку BAC |
| `height_cm` | PositiveIntegerField | Зріст у см |
| `weight_kg` | DecimalField(5,1) | Вага в кг — для розрахунку BAC |
| `is_adult_confirmed` | BooleanField | Підтвердження 18+ |
| `gdpr_consent` | BooleanField | Згода на обробку персональних даних |
| `favorite_scenarios` | M2M → Scenario | Обрані сценарії |
| `is_premium` | BooleanField | Статус Premium підписки |
| `premium_trial_end` | DateTimeField | Дата закінчення trial |
| `language` | CharField (uk/en) | Мова інтерфейсу |
| `theme` | CharField (dark/light/auto) | Тема |
| `notifications_enabled` | BooleanField | Загальні сповіщення |
| `email_notifications` | BooleanField | Email сповіщення |
| `push_notifications` | BooleanField | Push сповіщення |
| `profile_visible` | BooleanField | Видимість профілю |
| `show_in_leaderboard` | BooleanField | Показувати в лідерборді |

**Методи:** `get_display_name()`, `get_friends()`, `get_pending_requests()`, `get_friend_event_count(friend)`

#### FriendRequest
| Поле | Тип | Опис |
|---|---|---|
| `from_user` | FK → User | Хто відправив |
| `to_user` | FK → User | Кому відправив |
| `status` | CharField | pending / accepted / rejected |

#### Notification
| Поле | Тип | Опис |
|---|---|---|
| `user` | FK → User | Отримувач |
| `notification_type` | CharField | friend_request / event_invite / event_update / achievement / system |
| `title`, `message` | CharField/TextField | Зміст |
| `is_read` | BooleanField | Прочитано чи ні |

### 4.2. events — Напої, страви, сценарії, події

#### DrinkCategory
Категорії напоїв (вино, пиво, міцне, безалкогольне та інші — 14 категорій у seed).

#### DrinkTag
Теги напоїв: червоне, сухе, ігристе, яблучне, кола тощо (14 тегів у seed).

#### Drink
| Поле | Тип | Опис |
|---|---|---|
| `slug` | SlugField (unique) | URL-slug |
| `name` | CharField | Назва |
| `category` | FK → DrinkCategory | Категорія |
| `strength` | CharField | strong / regular / non_alcoholic |
| `abv` | DecimalField(4,1) | Міцність у % об. |
| `tags` | M2M → DrinkTag | Теги |
| `image` | ImageField | Зображення |

#### Dish
| Поле | Тип | Опис |
|---|---|---|
| `slug`, `name`, `description` | — | Базова інформація |
| `recipe_text` | TextField | Рецепт/інструкція |
| `difficulty` | CharField | easy / medium / hard |
| `drinks` | M2M → Drink | Які напої підходять |
| `ingredients` | M2M → Ingredient (through DishIngredient) | Інгредієнти |

#### Ingredient
| Поле | Опис |
|---|---|
| `name` | Назва (unique) |
| `category` | food / other |
| `default_unit` | pcs / g / kg / ml / l |
| `is_alcoholic` | Чи алкогольний |

#### DishIngredient (through table)
`dish` + `ingredient` + `qty_per_person` + `unit` — кількість на 1 порцію.

#### Scenario
Готові сценарії подій.

| Поле | Тип | Опис |
|---|---|---|
| `slug`, `name`, `description` | — | Базові |
| `category` | CharField | romantic / sport / party / budget / friends / family / holiday / other |
| `icon` | CharField | Емодзі (🎉) |
| `drinks` | M2M → Drink | Доступні напої |
| `prep_text` | TextField | Рекомендації по підготовці |
| `during_text` | TextField | Поради під час події |
| `after_text` | TextField | Поради по відновленню |

#### Event
Головна сутність — подія.

| Поле | Тип | Опис |
|---|---|---|
| `user` | FK → User | Організатор |
| `scenario` | FK → Scenario | За яким сценарієм |
| `drinks` | M2M → Drink | Обрані напої |
| `dishes` | M2M → Dish | Обрані страви |
| `cocktails` | M2M → Cocktail | Обрані коктейлі |
| `title` | CharField | Назва події |
| `date` | DateField | Дата (валідація: не в минулому) |
| `start_time`, `end_time` | TimeField | Час |
| `people_count` | PositiveIntegerField | Кількість людей (1-100) |
| `duration_hours` | PositiveIntegerField | Тривалість (1-72) |
| `intensity` | CharField | low / medium / high |
| `notes` | TextField | Нотатки |
| `location_name`, `location_address` | CharField | Місце проведення |
| `location_lat`, `location_lng` | DecimalField | Координати |
| `is_finished` | BooleanField | Подія завершена |
| `user_rating` | PositiveIntegerField | Оцінка 1-5 |
| `feedback` | TextField | Відгук |

**Методи:** `get_participants()`, `get_average_rating()`

#### EventParticipant
| Поле | Тип | Опис |
|---|---|---|
| `event` | FK → Event | Подія |
| `participant` | FK → User | Учасник |
| `status` | CharField | pending / accepted / declined / maybe |
| `role` | CharField | head / participant |
| `rating`, `feedback` | — | Оцінка учасника |

**Методи:** `accept()`, `decline()`

#### EventMessage
Обговорення події: `event` + `user` + `text` + `created_at`.

#### AlcoholLog (Алко-щоденник)
| Поле | Тип | Опис |
|---|---|---|
| `user` | FK → User | Користувач |
| `event` | FK → Event (optional) | Прив'язана подія |
| `drink` | FK → Drink (optional) | Напій |
| `taken_at` | DateTimeField | Час вживання |
| `volume_ml` | PositiveIntegerField | Об'єм у мл |
| `abv` | DecimalField | Міцність (або береться з Drink) |
| `bac_estimate` | DecimalField | BAC у проміле |

**Формула BAC (Widmark):**
```
pure_alcohol_g = volume_ml × (abv/100) × 0.789
BAC = pure_alcohol_g / (r × weight_kg × 10)
BAC_promille = BAC × 10
```
Де `r` — коефіцієнт Widmark: 0.68 для чоловіків, 0.55 для жінок, 0.6 усереднений.

### 4.3. recipes — Коктейлі

#### Cocktail
| Поле | Тип | Опис |
|---|---|---|
| `name`, `slug`, `description` | — | Базові |
| `instructions` | TextField | Рецепт приготування |
| `image` | ImageField | Зображення |
| `category` | CharField | 12 типів: shot, classic, tiki, sour, fizz, highball, martini, frozen, hot, punch, spritz, other |
| `strength` | CharField | light / medium / strong / very_strong / non_alcoholic |

**Computed:** `avg_rating` — @property з агрегації CocktailReview.

#### CocktailIngredient
`cocktail` + `ingredient` + `amount` + `unit`.

#### CocktailReview
`cocktail` + `user` + `rating` (1-5) + `text` — unique_together('cocktail', 'user').

### 4.4. gamification — Гейміфікація

#### UserScore
`user` (OneToOne) + `points_total`.

#### Achievement
`code` (unique) + `title` + `description` + `points_reward`.

#### UserAchievement
`user` + `achievement` + `earned_at` — unique_together.

#### Challenge
| Поле | Опис |
|---|---|
| `code` | Унікальний ідентифікатор |
| `title`, `description` | Текст |
| `difficulty` | easy / medium / hard |
| `points_reward` | Кількість балів |
| `target_count` | Скільки разів потрібно виконати |
| `icon` | Емодзі |

#### UserChallenge
`user` + `challenge` + `progress` + `status` (in_progress / completed / claimed).

### 4.5. shopping — Списки покупок

#### ScenarioSupplyTemplate
Шаблон: якому сценарію яка кількість товарів потрібна.

| Поле | Опис |
|---|---|
| `scenario` | FK → Scenario |
| `stage` | prep / during / recovery |
| `name` | Назва товару |
| `category` | alcohol / food / water / ice / other |
| `unit` | pcs / ml / l / g / kg |
| `qty_per_person_per_hour` | Кількість на 1 людину на 1 годину |

**Формула розрахунку:** `qty = qty_per_person_per_hour × people_count × duration_hours`

Плюс додаються інгредієнти з обраних страв (DishIngredient × people_count) та коктейлів (CocktailIngredient × people_count).

#### ShoppingList, ShoppingItem
Збережені списки покупок користувача.

### 4.6. places — Карта закладів

#### Place
`name` + `kind` (bar/shop/other) + `lat/lon` + `city` + `address` + `url`.

#### Promotion
`place` + `title` + `description` + `valid_from/to` + `source_url` — акції закладів.

### 4.7. social — Соціальна мережа

FriendRequest та Notification описані в accounts. Social app надає в'юшки для пошуку, заявок, та лідерборду друзів.

---

## 5. Автентифікація та безпека

### 5.1. Модель автентифікації

- **Email-based логін**: `AUTH_USER_MODEL = "accounts.User"`, логін по email (не username)
- **Три бекенди автентифікації:**
  1. `accounts.backends.EmailBackend` — email + password
  2. `accounts.backends.GoogleOAuth2Backend` — Google OAuth2
  3. `django.contrib.auth.backends.ModelBackend` — стандартний (fallback)

### 5.2. Google OAuth2

Повністю реалізований без зовнішніх бібліотек (без django-allauth):

1. Фронтенд завантажує Google Sign-In JS SDK
2. Користувач авторизується через Google popup
3. ID Token надсилається на `/accounts/google-auth/`
4. Сервер верифікує токен через `https://oauth2.googleapis.com/tokeninfo`
5. Створюється (або знаходиться) User + Profile
6. Автоматично ставиться `is_adult_confirmed=True` та `gdpr_consent=True`

### 5.3. Хешування паролів

```python
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",  # Primary
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",  # Fallback
    ...
]
```

Argon2 — переможець конкурсу Password Hashing Competition, стійкий до GPU/ASIC атак.

### 5.4. JWT (REST API)

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
```

- Access token: 60 хвилин
- Refresh token: 7 днів
- При оновленні refresh token'а — старий потрапляє у blacklist

### 5.5. CAPTCHA

- **hCaptcha** на формі реєстрації
- Математична captcha (`SimpleCaptchaMixin`) — задачі на додавання/віднімання з HMAC-verified хешем

### 5.6. Rate Limiting

Кастомна реалізація на основі Django cache:

| Конфігурація | Кількість | Період |
|---|---|---|
| Логін | 5 спроб | 300 сек |
| Реєстрація | 3 спроби | 600 сек |
| Скидання пароля | 3 спроби | 600 сек |
| Видалення акаунту | 3 спроби | 600 сек |

При перевищенні ліміту повертається HTTP 429 із повідомленням українською.

### 5.7. Content Security Policy (CSP)

Middleware `CSPNonceMiddleware` додає nonce до кожного запиту:

```python
CSP_POLICY = {
    "default-src": "'self'",
    "script-src": f"'self' 'nonce-{{nonce}}' https://accounts.google.com ...",
    "style-src": f"'self' 'nonce-{{nonce}}' https://fonts.googleapis.com ...",
    "img-src": "'self' data: https: blob:",
    "font-src": "'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com",
    "connect-src": "'self' https://accounts.google.com ...",
    "frame-src": "https://accounts.google.com",
    "object-src": "'none'",
    "base-uri": "'self'",
}
```

### 5.8. Production Security

```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

### 5.9. 2FA для адмін-панелі

```python
from django_otp.admin import OTPAdminSite
admin.site.__class__ = OTPAdminSite
```

Адмін-панель захищена TOTP-автентифікацією (Google Authenticator тощо).

### 5.10. Декоратори доступу

- `@adult_required` — перевіряє `profile.birth_date` (18+), `is_adult_confirmed`, `gdpr_consent`; інакше → redirect на personal_data
- `@premium_required` — перевіряє `profile.is_premium`; інакше → redirect на plan_choice

### 5.11. @require_POST

Всі mutation views (видалення, створення, зміна статусу) захищені декоратором `@require_POST` для захисту від CSRF GET-запитів.

---

## 6. Middleware

| # | Middleware | Опис |
|---|---|---|
| 1 | SecurityMiddleware | Django security headers |
| 2 | SessionMiddleware | Сесії |
| 3 | CommonMiddleware | URL normalization |
| 4 | CsrfViewMiddleware | CSRF-захист |
| 5 | AuthenticationMiddleware | Автентифікація |
| 6 | MessageMiddleware | Flash-повідомлення |
| 7 | XFrameOptionsMiddleware | X-Frame-Options header |
| 8 | RequestLogMiddleware | Логування всіх HTTP-запитів |
| 9 | CSPNonceMiddleware | Content Security Policy nonces |
| 10 | SecurityLoggingMiddleware | Логування підозрілих запитів |

---

## 7. REST API

### 7.1. Ендпоінти

```
/api/v1/auth/register/      POST — Реєстрація (email + password)
/api/v1/auth/login/          POST — Логін → JWT tokens
/api/v1/auth/token/refresh/  POST — Оновлення access token
/api/v1/auth/profile/        GET/PUT — Профіль поточного користувача
```

### 7.2. Серіалізатори

- `RegisterSerializer` — email, password (write_only), створює User + Profile
- `LoginSerializer` — email, password, повертає tokens + user data
- `ProfileSerializer` — read/write профіль (birth_date, sex, weight_kg, height_cm, display_name, unique_tag)

### 7.3. Permissions

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
```

---

## 8. Сервіси (Business Logic)

### 8.1. Gamification Service (`gamification/services.py`)

**award_points(user, action, multiplier=1)** — нараховує бали за 20+ дій:

| Дія | Бали | Опис |
|---|---|---|
| `event_create` | 10 | Створення події |
| `event_complete` | 20 | Завершення події (організатор) |
| `event_rate` | 5 | Оцінка своєї події |
| `event_invite` | 3 | Запрошення друга |
| `event_accept_invite` | 5 | Прийняття запрошення |
| `event_participate` | 10 | Участь у завершеній події |
| `friend_add` | 5 | Додавання друга |
| `profile_complete` | 15 | Заповнення профілю |
| `diary_entry` | 3 | Запис у щоденнику |
| `cocktail_view` | 1 | Перегляд коктейлю |
| `daily_login` | 2 | Щоденний вхід |
| `streak_7_days` | 20 | 7 днів підряд |
| `streak_30_days` | 100 | 30 днів підряд |
| `quiz_correct` | 5 | Правильна відповідь у вікторині |
| `shopping_list_create` | 5 | Створення списку покупок |
| `premium_subscribe` | 50 | Підписка Premium |

**Система рангів:**

| Бали | Ранг | Іконка |
|---|---|---|
| 0 | Тверезий Новачок | 🥛 |
| 100 | Перший Келих | 🍷 |
| 300 | Весела Чарка | 🥃 |
| 500 | Барний Філософ | 🍺 |
| 1000 | Душа Компанії | 🎉 |
| 2000 | Похмільний Воїн | 🤕 |
| 5000 | Майстер Тостів | 🏆 |
| 10000 | Легенда Застілля | 👑 |

**Автоматичні досягнення:**
- За бали: 100 (Початківець 🌱), 500 (Активіст ⭐), 1000 (Ентузіаст 🏆), 5000 (Легенда 👑)
- За події: 1 (Перша подія 🎉), 5 (Організатор 📅), 10 (Досвідчений 🎭), 50 (Майстер подій 🏅)

### 8.2. Shopping Service (`shopping/services.py`)

**build_shopping_items()** — розраховує список покупок:

1. Бере шаблони `ScenarioSupplyTemplate` для обраного сценарію + етапів
2. Формула: `qty = qty_per_person_per_hour × people_count × duration_hours`
3. Додає інгредієнти з обраних страв: `qty_per_person × people_count`
4. Додає інгредієнти з обраних коктейлів: `amount × people_count`
5. Групує по `(name, category, unit)` та сумує кількості

### 8.3. Email Service (`accounts/emails.py`)

Три функції для email-сповіщень:

1. **`send_welcome_email(user)`** — вітальний лист після реєстрації
2. **`send_event_invitation_email(participant, event, inviter)`** — запрошення на подію
3. **`send_invitation_response_email(participant, event, accepted)`** — відповідь на запрошення

Всі листи перевіряють `profile.email_notifications` перед відправкою. Використовують branded HTML-шаблони з `templates/emails/`.

### 8.4. Cache Service (`events/cache.py`)

- Кешування сценаріїв, напоїв, категорій напоїв (5-хвилинний TTL)
- Signal-based invalidation: `post_save`/`post_delete` на Scenario, Drink, DrinkCategory → invalidate відповідного кешу

### 8.5. BAC Calculator (in `events/views/utils.py`)

**`build_recommendations_placeholder()`** — розраховує:
- Рекомендований об'єм алкоголю на основі ваги, статі, інтенсивності
- Кількість води (правило 1:1 з алкоголем)
- Рекомендації по їжі
- Оцінку BAC
- Час елімінації алкоголю з організму

**`build_recovery_advice()`** — поради по відновленню після події.

---

## 9. Views (детально)

### 9.1. accounts/views.py

| View | Метод | Опис |
|---|---|---|
| `SignUpView` | GET/POST | Реєстрація (email, пароль, captcha, 18+, GDPR). Redirect → personal_data. Автологін після реєстрації. Відправка welcome email. |
| `google_auth_view` | POST | Google OAuth2 — верифікація токена → створення/логін користувача |

### 9.2. pages/views.py

| View | URL | Опис |
|---|---|---|
| `home_view` | `/` | Головна сторінка |
| `dashboard_view` | `/dashboard/` | Дашборд із статистикою |
| `profile_view` | `/me/` | Профіль поточного користувача |
| `personal_data_view` | `/personal-data/` | Форма персональних даних (birth_date, вага, зріст, стать) |
| `calculator_view` | `/calculator/` | Калькулятор BAC |
| `notifications_view` | `/notifications/` | Сповіщення |
| `plan_choice_view` | `/premium/` | Вибір плану Premium |
| `payment_form_view / payment_success_view` | — | Демо-оплата Premium |
| `delete_account_view` | `/delete-account/` | Видалення акаунту (підтвердження паролем + "видалити") |
| `settings_view` | `/settings/` | Налаштування (сповіщення, приватність, тема) |

### 9.3. events/views/

**events.py:**
| View | Опис |
|---|---|
| `event_list` | Список подій (активні + архів) |
| `event_create_from_scenario` | Багатокрокове створення: сценарій → напої → страви → деталі |
| `event_edit` | Редагування події з M2M напоями/стравами/коктейлями |
| `event_delete` | Видалення (@require_POST) |
| `event_detail` | Деталі + рекомендації + поради по відновленню |
| `event_recommendations_preview` | AJAX preview рекомендацій |
| `event_location` | Карта місця проведення |
| `event_feedback` | Оцінка та відгук після події |
| `event_discussion` | Чат/обговорення події |

**participants.py:**
| View | Опис |
|---|---|
| `event_participants` | Список учасників + пошук друзів для запрошення |
| `event_invite_friend` | Запрошення конкретного друга + email notification |
| `event_remove_participant` | Видалення учасника |
| `event_toggle_admin` | Переключення ролі head/participant |
| `event_invitation_response` | Прийняти/відхилити + email notification організатору |
| `event_finish` | Завершення події |
| `my_invitations` | Мої запрошення |
| `event_leave` | Покинути подію |

**diary.py:**
| View | Опис |
|---|---|
| `diary_list` | Повний алко-щоденник зі статистикою: BAC-графіки, розподіл по годинах/днях тижня, топ напоїв, трендів |
| `diary_detail` | Деталі запису |
| `diary_add` | Новий запис |

**scenarios.py:**
| View | Опис |
|---|---|
| `scenario_list` | Список сценаріїв з фільтрацією по категоріях + обрані |
| `toggle_favorite_scenario` | Toggle обраний сценарій |
| `scenario_detail` | Деталі: вибір напоїв, розрахунок порцій, коктейлі по категоріях |

### 9.4. recipes/views.py

| View | Опис |
|---|---|
| `cocktail_list` | Фільтрація: назва, алкоголь, категорія, міцність, рейтинг + AJAX |
| `cocktail_detail` | Деталі + додавання до подій + огляд |
| `cocktail_search_by_ingredients` | Пошук коктейлів по інгредієнтах (AND-логіка) + AJAX |
| `add_cocktail_to_event` | M2M cocktail→event із перевіркою доступу |
| `add_cocktail_review` | Створення/оновлення відгуку (1-5 зірок) |
| `ai_sommelier` / `ai_sommelier_api` | **Premium**: AI-підбір напоїв на основі сценарію, смакових уподобань, міцності, настрою, історії |

### 9.5. social/views.py

| View | Опис |
|---|---|
| `friends_list` | Список друзів |
| `search_users` | Пошук по тегу (#ABC123) або email |
| `send_friend_request` | Відправка заявки |
| `accept/reject_friend_request` | Прийняти/відхилити |
| `friends_leaderboard` | Таблиця лідерів серед друзів |
| `user_profile_by_tag` | Публічний профіль з статистикою |

### 9.6. gamification/views.py

| View | Опис |
|---|---|
| `leaderboard` | Топ-3 подіум + таблиця 15 користувачів |
| `my_achievements` | Мої досягнення |
| `challenges_list` | Список челенджів |
| `claim_challenge_reward` | Отримати нагороду за виконаний челендж |
| `cocktail_quiz` | Сторінка вікторини |
| `cocktail_quiz_question` | генерація випадкового питання (4 варіанти) |
| `cocktail_quiz_answer` | Перевірка відповіді (+5 балів за правильну) |

### 9.7. stats/views.py

| View | Опис |
|---|---|
| `dashboard` | Всеосяжна статистика: кількість подій, записів, щомісячні графіки, BAC, гейміфікація |
| `export_pdf_report` | **Premium**: PDF-звіт з кирилицею (DejaVuSans) — таблиці подій, щоденника, гейміфікації |

### 9.8. places/views.py

Карта закладів Києва (бари, магазини) з акційними пропозиціями.

### 9.9. shopping/views.py

Калькулятор списку покупок на основі сценарію, подій, страв та коктейлів. Збереження/перегляд списків.

---

## 10. Форми

### accounts/forms.py

- **`SimpleCaptchaMixin`** — математична captcha (додавання/віднімання, HMAC-хеш для верифікації)
- **`SignUpForm`** — email-only реєстрація, auto-generateing username; перевірка на дублікат email (case-insensitive); пароль 8+ символів
- **`EmailAuthenticationForm`** — логін по email (поле username рендериться як email input)

### events/forms.py

- **`ScenarioDrinkForm`** — вибір напоїв, коктейлів, страв; кількість людей, тривалість, інтенсивність, складність
- **`EventCreateFromScenarioForm`** — назва, дата (min=today), people_count (1-100), duration_hours (1-72), нотатки
- **`EventUpdateForm`** — повне редагування з M2M drink/dish/cocktail
- **`AlcoholLogForm`** — запис у щоденник

### pages/forms.py

- **`ProfileForm`** — birth_date, sex, height_cm, weight_kg, is_adult_confirmed, gdpr_consent; валідація віку 18+

### shopping/forms.py

- **`ShoppingCalcForm`** — сценарій, подія, страви, коктейлі, етапи, people_count, duration_hours, інтенсивність; auto-заповнення з обраної події

---

## 11. Signals

| Signal | Модель | Дія |
|---|---|---|
| `post_save` on User | User | Автоматичне створення Profile через `get_or_create` |
| `post_save`/`post_delete` on Scenario, Drink, DrinkCategory | — | Інвалідація кешу (events/cache.py) |

---

## 12. Management Commands

| Команда | App | Опис |
|---|---|---|
| `seed_scenarios` | events | Заповнення сценаріїв (8+ типів), коктейлів з інгредієнтами, челенджів, досягнень |
| `seed_drinks` | events | Заповнення категорій напоїв (14), тегів (14), ~30+ напоїв, прив'язка напоїв до сценаріїв |
| `seed_dishes` | events | Заповнення інгредієнтів (60+), страв із кількістю інгредієнтів |
| `seed_places` | places | Заповнення закладів Києва (бари, магазини) з акціями |

Запуск: `python manage.py seed_scenarios` та інші.

---

## 13. Email-система

### Налаштування (Gmail SMTP)

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailSmtpBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=delifeboss@gmail.com
EMAIL_HOST_PASSWORD=<App Password>
DEFAULT_FROM_EMAIL=Alechemy <delifeboss@gmail.com>
```

### Типи email

1. **Welcome Email** — після реєстрації, привітання + посилання на налаштування профілю
2. **Event Invitation** — при запрошенні на подію: деталі події + посилання
3. **Invitation Response** — організатору при прийнятті/відхиленні запрошення
4. **Password Reset** — стандартний Django з branded HTML-шаблоном

### Шаблони

Всі email використовують branded темну тему Alechemy із зеленим акцентом (`#4ecb71`), розташовані в `templates/emails/`.

---

## 14. Тестування

### Конфігурація

```python
# alechemy/settings_test.py
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # швидкість
CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

### Фікстури (conftest.py)

```python
@pytest.fixture
def adult_user(db):
    # User з профілем: birth_date=2000-01-01, gdpr_consent=True, is_adult_confirmed=True
```

Фікстури: `client`, `user`, `adult_user`, `authenticated_client`, `admin_user`, `other_user`, `scenario`, `drink`, `dish`, `event`, `friend_request`.

### Тестові файли

| Файл | Покриття |
|---|---|
| `tests/test_accounts.py` | Реєстрація, логін, профіль, Google OAuth |
| `tests/test_events.py` | Сценарії, події, учасники, щоденник |
| `tests/test_security.py` | CSRF, rate limiting, доступ, CSP |
| `tests/test_social.py` | Друзі, заявки, лідерборд |
| `tests/test_gamification.py` | Бали, досягнення, челенджі, вікторина |

Запуск: `pytest --ds=alechemy.settings_test`

---

## 15. Templates

```
templates/
├── base.html                          — Базовий layout
├── emails/
│   ├── welcome.html                   — Welcome email
│   ├── event_invitation.html          — Запрошення на подію
│   └── invitation_response.html       — Відповідь на запрошення
├── events/
│   ├── scenario_list/detail.html      — Сценарії
│   ├── event_list/create/edit/detail  — Управління подіями
│   ├── event_participants.html        — Учасники
│   ├── diary_list/add/detail.html     — Алко-щоденник
│   └── partials/                      — AJAX-фрагменти
├── pages/
│   ├── home/dashboard/profile.html    — Головні сторінки
│   ├── personal_data.html             — Персональні дані
│   ├── calculator.html                — BAC-калькулятор
│   └── premium/                       — Сторінки Premium
├── registration/
│   ├── login/signup.html              — Автентифікація
│   ├── password_reset_*.html          — Скидання пароля
│   └── welcome/start.html            — Onboarding
├── shopping/                          — Списки покупок
├── gamification/templates/gamification/
│   ├── leaderboard/achievements.html  — Рейтинги
│   └── cocktail_quiz.html             — Вікторина
├── social/templates/social/           — Друзі, профілі
├── places/templates/places/           — Карта, заклади
├── recipes/templates/recipes/         — Коктейлі, AI
└── stats/templates/stats/             — Статистика
```

---

## 16. Скрипти

| Скрипт | Платформа | Опис |
|---|---|---|
| `scripts/deploy.sh` | Linux | Production deploy: перевірка .env.prod + SSL → docker build → start → migrate + collectstatic + check --deploy |
| `scripts/backup.sh` | Linux | pg_dump → gzip, ротація 30 днів |
| `scripts/restore.sh` | Linux | Відновлення БД: підтвердження, drop+create, підтримка .gz |
| `scripts/backup.ps1` | Windows | Еквівалент backup.sh для PowerShell |
| `scripts/restore.ps1` | Windows | Еквівалент restore.sh для PowerShell |

---

## 17. Логування

7 хендлерів логування:

| Handler | Ціль | Рівень |
|---|---|---|
| `console` | stdout | INFO |
| `file_django` | logs/django.log | WARNING |
| `file_security` | logs/security.log | INFO |
| `file_requests` | logs/requests.log | INFO |
| `file_db_queries` | logs/db_queries.log | DEBUG |
| `file_app` | logs/app.log | DEBUG |
| `sentry` | Sentry (production) | ERROR |

**Spеціальні логери:**
- `django.db.backends` → SQL-запити
- `alechemy.security` → підозрілі запити
- `alechemy.requests` → всі HTTP-запити
- `alechemy.app` → application logic

---

## 18. Локалізація

- `LANGUAGE_CODE = "uk"` — українська за замовчуванням
- `LocaleMiddleware` видалено, щоб завжди використовувалась українська незалежно від браузера
- Підтримка: `uk` (українська), `en` (англійська)
- Файли перекладів: `locale/uk/`, `locale/en/`
- `fill_translations.py` — скрипт для заповнення порожніх перекладів

---

## 19. Nginx (Production)

- Reverse proxy до Gunicorn
- Обслуговування static/media файлів
- SSL (сертифікати у `nginx/ssl/`)
- Rate limiting
- Gzip-стиснення
- Security headers

---

## 20. Змінні середовища (.env)

```env
# Django
DEBUG=True
DJANGO_SECRET_KEY=<secret>
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=alechemy
DB_USER=postgres
DB_PASSWORD=<password>
DB_HOST=db
DB_PORT=5432

# Email (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailSmtpBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<app_password>
DEFAULT_FROM_EMAIL=Alechemy <email>

# Google OAuth2
GOOGLE_OAUTH2_CLIENT_ID=<client_id>
GOOGLE_OAUTH2_CLIENT_SECRET=<client_secret>

# Sentry (production)
SENTRY_DSN=<dsn>

# hCaptcha
HCAPTCHA_SITEKEY=<key>
HCAPTCHA_SECRET=<secret>

# Domain
SITE_DOMAIN=localhost:8000
```

---

## 21. Запуск проєкту

### Development

```bash
docker-compose up --build
```

Це запускає:
1. PostgreSQL (port 5432)
2. Django dev server (port 8000)
3. Автоматичні міграції через `docker-entrypoint.dev.sh`

### Production

```bash
./scripts/deploy.sh
```

Або вручну:
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### Заповнення даними

```bash
docker exec -it alechemy_web python manage.py seed_scenarios
docker exec -it alechemy_web python manage.py seed_drinks
docker exec -it alechemy_web python manage.py seed_dishes
docker exec -it alechemy_web python manage.py seed_places
```

### Тести

```bash
docker exec -it alechemy_web pytest --ds=alechemy.settings_test
```

---

## 22. Ключові бізнес-правила

1. **Вік 18+** — обов'язковий для доступу до основних функцій (перевіряється через `birth_date`)
2. **GDPR** — згода на обробку даних обов'язкова при реєстрації
3. **BAC** — приблизна оцінка за формулою Widmark, не є медичним висновком
4. **Premium** — AI Сомельє та PDF-експорт доступні тільки для Premium-підписників
5. **Рейтинг** — кожен користувач може залишити лише один відгук на коктейль (unique_together)
6. **Друзі** — двостороння система: запит → прийняття. Можна шукати по тегу або email
7. **Список покупок** — автоматичний розрахунок на основі формул (людини × години × коефіцієнт)
8. **Email сповіщення** — відправляються тільки якщо у профілі увімкнено `email_notifications`
9. **Password reset** — Django не повідомляє, якщо email не знайдений у базі (захист від перерахування)
10. **Multi-stage подія** — організатор → сценарій → напої/страви/коктейлі → деталі → учасники
