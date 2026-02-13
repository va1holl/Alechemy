# 🍸 ALECHEMY — Презентація проекту

## Розумний помічник для планування вечірок з алкоголем

---

## 📌 Загальний опис

**Alechemy** — це повнофункціональний веб-застосунок для планування подій з алкоголем. Застосунок допомагає користувачам організовувати вечірки, розраховувати кількість напоїв та їжі, відстежувати споживання алкоголю, знаходити заклади поруч, а також взаємодіяти з друзями через соціальні функції та гейміфікацію.

**Цільова аудиторія:** люди віком 18+, які планують вечірки, хочуть контролювати своє споживання алкоголю або шукають рекомендації з коктейлів та закладів.

---

## 🎯 Ключові функції

### 1. 📅 Події та сценарії
- Створення подій з вибором готового сценарію (День народження, Корпоратив, Побачення, тощо)
- Налаштування кількості гостей, напоїв, страв і тривалості
- Автоматичні рекомендації по підготовці, проведенню та відновленню після події
- Запрошення друзів на події

### 2. 🧮 Калькулятор алкоголю (BAC)
- Розрахунок приблизного рівня алкоголю в крові (Blood Alcohol Content)
- Враховує вагу, стать та кількість випитого
- Допомагає планувати безпечне споживання

### 3. 📊 Алко-щоденник
- Журналювання спожитих напоїв
- Історія споживання за дні/тижні/місяці
- Аналітика та графіки

### 4. 🗺 Карта закладів
- Інтерактивна карта барів, магазинів, ресторанів
- Інформація про акції та знижки
- Фільтрація за типом закладу та локацією

### 5. 🍹 База коктейлів
- 100+ коктейлів з детальними рецептами
- Категоризація (класичні, шоти, тікі, сауери тощо)
- Рейтинги та відгуки користувачів
- Пошук за інгредієнтами

### 6. 🛒 Список покупок (Premium)
- Автоматичний розрахунок продуктів для події
- Базується на кількості гостей, тривалості та інтенсивності
- Інгредієнти для обраних коктейлів та страв

### 7. 🏆 Гейміфікація
- **Бали** — за активність (створення подій, відгуки, запрошення друзів)
- **Досягнення (Ачивки)** — за виконання певних умов
- **Челенджі** — щотижневі та спеціальні завдання
- **Таблиця лідерів** — змагання з друзями та глобально

### 8. 👥 Соціальні функції
- Система друзів з пошуком за унікальним тегом (#ABC123) або email
- Запрошення на події
- Спільне редагування подій
- Публічні профілі

---

## 🏗 Архітектура та технології

### Технологічний стек

| Категорія | Технологія | Версія | Обґрунтування |
|-----------|------------|--------|---------------|
| **Backend Framework** | Django | 5.2 | Зрілий, безпечний фреймворк з вбудованою ORM, адмінкою, системою аутентифікації. Ідеальний для швидкої розробки веб-застосунків. |
| **API** | Django REST Framework | 3.16 | Стандарт для побудови REST API на Django. Серіалізатори, аутентифікація, документація. |
| **База даних** | PostgreSQL | 16 | Надійна реляційна БД з повнотекстовим пошуком, JSON підтримкою, відмінною продуктивністю. |
| **Кешування** | Redis | 7 | Швидкий in-memory кеш для сесій, rate limiting та кешування запитів. |
| **JWT Auth** | djangorestframework-simplejwt | 5.5 | Безпечна токен-аутентифікація для API з підтримкою refresh токенів та blacklist. |
| **Password Hashing** | Argon2 | Latest | Переможець PHC (Password Hashing Competition), найбезпечніший алгоритм хешування. |
| **Web Server** | Gunicorn | 25 | WSGI сервер для production, підтримка воркерів, ефективне управління процесами. |
| **Reverse Proxy** | Nginx | 1.24 | SSL термінація, статика, балансування навантаження, захист від атак. |
| **Контейнеризація** | Docker + Compose | Latest | Консистентне середовище розробки та production, легкий деплой. |
| **2FA** | django-otp | 1.7 | Двофакторна аутентифікація для адмін-панелі (TOTP). |
| **CAPTCHA** | hCaptcha | 0.2 | Захист форм реєстрації/логіну від ботів. Privacy-friendly альтернатива reCAPTCHA. |
| **PDF Generation** | ReportLab | 4.4 | Генерація PDF звітів зі статистикою (Premium функція). |
| **Monitoring** | Sentry | 2.52 | Моніторинг помилок у production, алерти, трейсинг. |
| **Мова** | Python | 3.12 | Сучасна версія з покращеною продуктивністю та новими можливостями. |

### Архітектурна схема

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  Django Templates + CSS3 + Vanilla JS + Chart.js             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Web Server (Nginx)                       │
│  • SSL/TLS Termination  • Static Files  • Reverse Proxy      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               Application Server (Gunicorn)                  │
│  • WSGI Workers  • Process Management  • Load Balancing      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django Application                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ Accounts │ │  Events  │ │ Recipes  │ │ Shopping │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │Gamificat.│ │  Social  │ │  Places  │ │  Stats   │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌───────────────────────┐       ┌───────────────────────┐
│   PostgreSQL 16       │       │     Redis 7           │
│   • Primary DB        │       │   • Sessions          │
│   • Full-text Search  │       │   • Cache             │
└───────────────────────┘       │   • Rate Limiting     │
                                └───────────────────────┘
```

---

## 📦 Структура модулів

### accounts/ — Користувачі та авторизація
- **Функції:** реєстрація, логін, профіль, друзі, сповіщення
- **Моделі:** `User` (кастомний), `Profile`, `FriendRequest`, `Notification`
- **API:** JWT аутентифікація, CRUD профілю
- **Особливості:** 
  - Унікальні теги для пошуку друзів (#ABC123)
  - Підтвердження віку 18+
  - GDPR consent
  - Premium статус

### events/ — Події та сценарії
- **Функції:** створення подій, вибір сценарію, алко-щоденник
- **Моделі:** `Event`, `Scenario`, `Drink`, `Dish`, `DrinkCategory`, `AlcoholLog`
- **Особливості:**
  - 8 категорій сценаріїв (Побачення, Вечірка, Корпоратив, тощо)
  - Три етапи події (підготовка, під час, відновлення)
  - Автоматичний розрахунок напоїв на основі гостей та тривалості

### gamification/ — Гейміфікація
- **Функції:** бали, досягнення, челенджі, лідерборд
- **Моделі:** `UserScore`, `Achievement`, `UserAchievement`, `Challenge`, `UserChallenge`
- **Особливості:**
  - Автоматичне нарахування балів за дії
  - Прогрес-бари для челенджів
  - Глобальний та друзі-лідерборд

### recipes/ — База коктейлів
- **Функції:** список коктейлів, рецепти, відгуки, пошук
- **Моделі:** `Cocktail`, `CocktailIngredient`, `CocktailReview`
- **Категорії:** Класичний, Шот, Тікі, Сауер, Фіз, Хайбол, Мартіні, Заморожений, Гарячий, Пунш, Шпріц

### shopping/ — Список покупок
- **Функції:** генерація списку на основі події, ручне редагування
- **Моделі:** `ShoppingList`, `ShoppingItem`, `ScenarioSupplyTemplate`
- **Формула:** `кількість = qty_per_person_per_hour × люди × години × коефіцієнт_інтенсивності`

### places/ — Карта закладів
- **Функції:** карта, список закладів, акції
- **Моделі:** `Place`, `Promotion`
- **Типи:** Бар, Магазин, Інше

### stats/ — Статистика
- **Функції:** дашборд, графіки споживання, PDF звіти
- **Інтеграція:** Chart.js для візуалізації

### social/ — Соціальні функції
- **Функції:** пошук друзів, запити в друзі, рейтинг
- Моделі винесені в accounts/ для уникнення циклічних залежностей

---

## 🔐 Безпека

### Захист на рівні застосунку

| Механізм | Реалізація |
|----------|-----------|
| **Хешування паролів** | Argon2 (переможець PHC) |
| **CSRF захист** | Django CSRF middleware + SameSite cookies |
| **XSS захист** | Content Security Policy (CSP) middleware |
| **SQL Injection** | Django ORM (параметризовані запити) |
| **Rate Limiting** | Кастомний middleware + Redis |
| **Brute Force** | Обмеження спроб логіну |
| **2FA** | TOTP для адмін-панелі (django-otp) |
| **CAPTCHA** | hCaptcha на реєстрації/логіні |
| **Session Security** | HttpOnly, Secure, SameSite cookies |

### Production Security Headers

```python
# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = 31536000  # 1 рік
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### Content Security Policy (CSP)

Динамічний CSP з nonce для inline scripts:
```
default-src 'self';
script-src 'self' 'nonce-{random}' https://js.hcaptcha.com;
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
img-src 'self' data: https:;
font-src 'self' https://fonts.gstatic.com;
```

---

## 🌍 Локалізація (i18n)

- **Підтримувані мови:** Українська (uk), English (en)
- **Файли перекладів:** `locale/uk/`, `locale/en/`
- **Реалізація:** Django gettext, `{% trans %}` в шаблонах
- **Переключення:** через профіль користувача

---

## 🐳 Docker та деплой

### Development середовище

```yaml
services:
  web:
    build: .
    ports: ["8000:8000"]
    volumes: [".:/app"]  # Live reload
    depends_on: [db]
    
  db:
    image: postgres:16
    healthcheck: pg_isready
```

### Production середовище

```yaml
services:
  web:
    build: 
      dockerfile: Dockerfile.prod
    command: gunicorn alechemy.wsgi:application
    
  nginx:
    image: nginx:1.24
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl
      
  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### CI/CD Pipeline (рекомендований)

1. **Push to main** → GitHub Actions
2. **Linting** → flake8, black
3. **Tests** → pytest
4. **Build** → docker build
5. **Deploy** → SSH + docker-compose up

---

## 📊 Моделі даних (ER-діаграма)

```
User (1) ──── (1) Profile
  │                  │
  │                  ├── favorite_scenarios (M:N) ── Scenario
  │                  │
  │                  └── Premium status
  │
  ├── (1:N) ── Event ──── (M:N) ── Drink
  │               │
  │               ├── (M:N) ── Dish
  │               │
  │               └── (M:1) ── Scenario
  │
  ├── (1:N) ── AlcoholLog
  │
  ├── (1:N) ── ShoppingList
  │
  ├── (1:N) ── FriendRequest ── User
  │
  ├── (1:1) ── UserScore
  │
  ├── (1:N) ── UserAchievement ── Achievement
  │
  └── (1:N) ── UserChallenge ── Challenge

Cocktail ── (1:N) ── CocktailIngredient ── (N:1) ── Ingredient
    │
    └── (1:N) ── CocktailReview ── (N:1) ── User

Place ── (1:N) ── Promotion
```

---

## 🧪 Тестування

### Типи тестів

| Тип | Інструмент | Покриття |
|-----|------------|----------|
| Unit тести | pytest | Бізнес-логіка, сервіси |
| Integration | pytest-django | Views, API endpoints |
| Security | Custom tests | CSRF, XSS, injection |
| E2E | (планується) | Selenium/Playwright |

### Запуск тестів

```bash
# Всі тести
pytest

# З покриттям
pytest --cov=. --cov-report=html

# Конкретний модуль
pytest tests/test_accounts.py -v
```

### Приклад тесту

```python
@pytest.mark.django_db
def test_user_registration(client):
    response = client.post('/accounts/register/', {
        'email': 'test@example.com',
        'password1': 'SecurePass123!',
        'password2': 'SecurePass123!',
        'is_adult': True,
    })
    assert response.status_code == 302
    assert User.objects.filter(email='test@example.com').exists()
```

---

## 💎 Premium функції

| Функція | Звичайний | Premium |
|---------|:---------:|:-------:|
| Створення подій | ✅ | ✅ |
| Алко-щоденник | ✅ | ✅ |
| База коктейлів | ✅ | ✅ |
| Карта закладів | ✅ | ✅ |
| **Список покупок** | ❌ | ✅ |
| **PDF звіти** | ❌ | ✅ |
| **AI-сомельє** | ❌ | ✅ |
| **Розширена статистика** | ❌ | ✅ |

---

## 🚀 Майбутні плани

### v1.1
- [ ] Мобільний застосунок (React Native / Flutter)
- [ ] Push сповіщення
- [ ] Інтеграція з календарем

### v1.2
- [ ] AI-сомельє (OpenAI GPT)
- [ ] Сканер етикеток (ML)
- [ ] Розширений пошук закладів

### v2.0
- [ ] Маркетплейс напоїв
- [ ] Бронювання столиків
- [ ] Групові чати подій

---

## � REST API

### Аутентифікація

Всі API endpoints використовують JWT токени (Access + Refresh).

```bash
# Отримання токена
POST /api/v1/auth/token/
{
  "email": "user@example.com",
  "password": "secret"
}

# Відповідь
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",   # 15 хв
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."  # 7 днів
}

# Використання
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Основні Endpoints

| Endpoint | Метод | Опис | Auth |
|----------|-------|------|:----:|
| **Аутентифікація** ||||
| `/api/v1/auth/token/` | POST | Отримати JWT токен | ❌ |
| `/api/v1/auth/token/refresh/` | POST | Оновити access токен | ❌ |
| `/api/v1/auth/register/` | POST | Реєстрація | ❌ |
| `/api/v1/auth/me/` | GET | Дані користувача | ✅ |
| `/api/v1/auth/password/change/` | POST | Зміна пароля | ✅ |
| `/api/v1/auth/logout/` | POST | Logout (blacklist token) | ✅ |
| **Події** ||||
| `/events/api/events/search/` | GET | Пошук подій | ✅ |
| `/events/events/recommendations-preview/` | POST | Рекомендації | ✅ |

---

## �📈 Обґрунтування технічних рішень

### Чому Django?

1. **Швидка розробка** — вбудовані компоненти (ORM, Auth, Admin)
2. **Безпека** — CSRF, XSS, SQL injection захист з коробки
3. **Масштабованість** — перевірено на великих проектах (Instagram, Pinterest)
4. **Екосистема** — тисячі готових пакетів (DRF, django-otp, etc.)
5. **Документація** — одна з найкращих у індустрії

### Чому PostgreSQL?

1. **Надійність** — ACID транзакції, репліка
2. **Функціональність** — JSON, Full-text search, GIS
3. **Продуктивність** — оптимізатор запитів, індекси
4. **Масштабування** — read replicas, partitioning

### Чому Argon2?

1. **Безпека** — переможець Password Hashing Competition
2. **Захист від GPU атак** — memory-hard алгоритм
3. **Гнучкість** — налаштування time/memory cost
4. **Рекомендації** — OWASP рекомендує як #1 вибір

### Чому Docker?

1. **Консистентність** — однакове середовище dev/staging/prod
2. **Ізоляція** — кожен сервіс у своєму контейнері
3. **Простота деплою** — `docker-compose up` і готово
4. **Масштабування** — легко додати воркери

### Чому Server-Side Rendering (Django Templates)?

1. **SEO** — сторінки індексуються пошуковими системами
2. **Продуктивність** — менше JavaScript, швидший First Paint
3. **Простота** — один стек, один язик (Python)
4. **Безпека** — менша поверхня атаки (немає окремого API для SPA)

*Для майбутнього мобільного застосунку вже є REST API на DRF.*

---

## 👨‍💻 Команда

> _Вкажіть учасників команди тут_

---

## 📞 Контакти

> _Вкажіть контактну інформацію тут_

---

## 📝 Ліцензія

MIT License — вільне використання з зазначенням авторства.

---

*Документ створено: Лютий 2026*
*Версія проекту: 1.0.0*
