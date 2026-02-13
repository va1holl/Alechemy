# 🍸 Alechemy

**Розумний помічник для планування вечірок з алкоголем**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Alechemy — це повнофункціональний веб-застосунок для планування подій з алкоголем, розрахунку кількості напоїв та їжі, відстеження споживання алкоголю, гейміфікації та соціальної взаємодії з друзями.

---

## 📋 Зміст

- [Функціональність](#-функціональність)
- [Архітектура](#-архітектура)
- [Швидкий старт](#-швидкий-старт)
- [Production Deployment](#-production-deployment)
- [Структура проекту](#-структура-проекту)
- [API Reference](#-api-reference)
- [Безпека](#-безпека)
- [Тестування](#-тестування)
- [Локалізація](#-локалізація)

---

## ✨ Функціональність

### 🎯 Основні модулі

| Модуль | Опис | Premium |
|--------|------|:-------:|
| **📅 Події та сценарії** | Створення подій з вибором сценарію (День народження, Корпоратив тощо), налаштування гостей, напоїв та страв | - |
| **🧮 Калькулятор алкоголю** | Розрахунок приблизного BAC на основі ваги, статі та споживання | - |
| **📊 Алко-щоденник** | Відстеження споживання алкоголю з історією та аналітикою | - |
| **🗺 Карта закладів** | Інтерактивна карта барів, магазинів та ресторанів з акціями | - |
| **🍹 База коктейлів** | 100+ коктейлів з рецептами, інгредієнтами та рейтингами | - |
| **🛒 Список покупок** | Автоматичний розрахунок покупок для події | ✅ |
| **🤖 AI-сомельє** | Персоналізовані рекомендації напоїв на основі вподобань | ✅ |
| **📈 PDF-звіти** | Детальна аналітика та експорт статистики | ✅ |

### 🏆 Гейміфікація

- **Бали** — отримуйте бали за активність (створення подій, відгуки, запрошення друзів)
- **Досягнення (Ачивки)** — розблоковуйте нагороди за виконання умов
- **Челенджі** — виконуйте щотижневі та спеціальні завдання
- **Міні-ігри** — "Вгадай коктейль" та інші ігри для отримання бонусів
- **Рейтинг лідерів** — змагайтесь з друзями та глобально

### 👥 Соціальні функції

- Система друзів з пошуком за тегом/email
- Запрошення друзів на події
- Спільне редагування подій
- Рейтинг друзів
- Публічні профілі з унікальними тегами

---

## 🏗 Архітектура

### Технологічний стек

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
│  • WSGI  • Workers  • Process Management                     │
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

### Основні залежності

| Категорія | Технологія | Версія |
|-----------|------------|--------|
| Framework | Django | 5.2+ |
| API | Django REST Framework | 3.15+ |
| Database | PostgreSQL | 16 |
| Cache/Session | Redis | 7 |
| Auth | djangorestframework-simplejwt | 5.3+ |
| Password Hashing | Argon2 | Latest |
| Web Server | Gunicorn | 21+ |
| Reverse Proxy | Nginx | 1.24+ |
| Containerization | Docker + Compose | Latest |

---

## 🚀 Швидкий старт

### Вимоги

- Docker & Docker Compose v2+
- Git
- (Опційно) Python 3.12+ для локальної розробки

### Інсталяція (Development)

```bash
# 1. Клонуйте репозиторій
git clone https://github.com/your-username/alechemy.git
cd alechemy

# 2. Створіть файл оточення
cp .env.example .env
# Відредагуйте .env за потреби

# 3. Запустіть Docker контейнери
docker-compose up -d

# 4. Застосуйте міграції
docker exec alechemy_web python manage.py migrate

# 5. Заповніть базу тестовими даними
docker exec alechemy_web python manage.py seed_cocktails

# 6. Створіть суперкористувача
docker exec -it alechemy_web python manage.py createsuperuser

# 7. Відкрийте у браузері
# Застосунок: http://localhost:8000
# Адмінка: http://localhost:8000/admin/
```

### Локальна розробка (без Docker)

```bash
# 1. Створіть віртуальне оточення
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
.\venv\Scripts\activate  # Windows

# 2. Встановіть залежності
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Налаштуйте PostgreSQL та Redis локально
# Або використовуйте SQLite для швидкого тестування:
# DATABASE_URL=sqlite:///db.sqlite3

# 4. Запустіть міграції
python manage.py migrate

# 5. Запустіть сервер розробки
python manage.py runserver
```

---

## 🏭 Production Deployment

### Крок 1: Підготовка сервера

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose-v2 git ufw

# Налаштування firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Крок 2: Клонування та налаштування

```bash
# Клонуйте репозиторій
git clone https://github.com/your-username/alechemy.git /opt/alechemy
cd /opt/alechemy

# Створіть production оточення
cp .env.example .env.prod
```

### Крок 3: Конфігурація `.env.prod`

```env
# Django
DEBUG=False
SECRET_KEY=your-super-secret-key-here-min-50-chars
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=alechemy_prod
DB_USER=alechemy
DB_PASSWORD=strong-database-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Security
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Email (для відновлення паролів)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Крок 4: SSL сертифікати

```bash
# Варіант A: Let's Encrypt (рекомендовано)
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Скопіюйте сертифікати
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Варіант B: Власні сертифікати
# Покладіть fullchain.pem та privkey.pem в nginx/ssl/
```

### Крок 5: Запуск

```bash
# Збірка та запуск
docker-compose -f docker-compose.prod.yml up -d --build

# Застосування міграцій
docker exec alechemy_web python manage.py migrate

# Збір статики
docker exec alechemy_web python manage.py collectstatic --noinput

# Створення суперкористувача
docker exec -it alechemy_web python manage.py createsuperuser

# Заповнення початковими даними
docker exec alechemy_web python manage.py seed_cocktails
```

### Корисні команди

```bash
# Перегляд логів
docker-compose -f docker-compose.prod.yml logs -f web

# Перезапуск
docker-compose -f docker-compose.prod.yml restart web

# Оновлення коду
git pull
docker-compose -f docker-compose.prod.yml up -d --build

# Бекап бази даних
./scripts/backup.sh

# Відновлення з бекапу
./scripts/restore.sh backups/backup_2024-01-01.sql
```

---

## 📁 Структура проекту

```
alechemy/
├── 📁 accounts/              # Користувачі та авторизація
│   ├── models.py            # User, Profile, FriendRequest, Notification
│   ├── views.py             # Реєстрація, логін, профіль
│   ├── api_views.py         # REST API endpoints
│   ├── serializers.py       # DRF serializers
│   ├── forms.py             # Django forms + SimpleCaptchaMixin
│   ├── backends.py          # Email authentication backend
│   └── decorators.py        # @adult_required, @premium_required
│
├── 📁 alechemy/              # Головний модуль Django
│   ├── settings.py          # Налаштування проекту
│   ├── urls.py              # Головні URL routes
│   ├── middleware.py        # CSP, Security middleware
│   └── context_processors.py
│
├── 📁 events/                # Події та сценарії
│   ├── models.py            # Event, Scenario, Drink, Dish, AlcoholLog
│   ├── views/               # Розділені views по функціональності
│   │   ├── events.py        # CRUD подій
│   │   ├── scenarios.py     # Сценарії
│   │   ├── diary.py         # Алко-щоденник
│   │   ├── participants.py  # Учасники подій
│   │   └── utils.py         # Допоміжні функції
│   └── forms.py             # Форми подій
│
├── 📁 gamification/          # Гейміфікація
│   ├── models.py            # UserScore, Achievement, Challenge
│   ├── views.py             # Лідерборд, досягнення, міні-ігри
│   ├── services.py          # award_points() та бізнес-логіка
│   └── templates/           # Шаблони гейміфікації
│
├── 📁 health/                # Health check
│   └── views.py             # /health/ endpoint для моніторингу
│
├── 📁 pages/                 # Основні сторінки
│   ├── views.py             # Dashboard, Profile, Calculator, Premium
│   ├── forms.py             # Форми профілю
│   └── templates/           # Шаблони сторінок
│
├── 📁 places/                # Карта закладів
│   ├── models.py            # Place, Promotion
│   └── views.py             # Карта, деталі закладу
│
├── 📁 recipes/               # Коктейлі
│   ├── models.py            # Cocktail, CocktailIngredient, CocktailReview
│   ├── views.py             # Список, пошук, AI-сомельє
│   └── management/commands/ # seed_cocktails command
│
├── 📁 shopping/              # Список покупок
│   ├── models.py            # ShoppingList, ShoppingItem
│   ├── views.py             # Генерація та перегляд списків
│   └── services.py          # Логіка розрахунку
│
├── 📁 social/                # Соціальні функції
│   ├── views.py             # Друзі, пошук, рейтинг
│   └── templates/           # Шаблони
│
├── 📁 stats/                 # Статистика
│   ├── views.py             # Dashboard статистики
│   └── templates/           # Графіки та звіти
│
├── 📁 templates/             # Глобальні шаблони
│   ├── base.html            # Базовий шаблон
│   ├── partials/            # Перевикористовувані компоненти
│   └── registration/        # Шаблони авторизації
│
├── 📁 static/                # Статичні файли (dev)
│   ├── css/                 # Стилі
│   ├── js/                  # JavaScript
│   └── img/                 # Зображення
│
├── 📁 locale/                # Переклади
│   ├── uk/                  # Українська
│   └── en/                  # English
│
├── 📁 nginx/                 # Конфігурація Nginx
│   ├── nginx.conf
│   └── ssl/                 # SSL сертифікати
│
├── 📁 scripts/               # Скрипти деплою
│   ├── backup.sh            # Бекап БД
│   ├── restore.sh           # Відновлення
│   └── deploy.sh            # Деплой скрипт
│
├── 📁 tests/                 # Тести
│   ├── conftest.py          # Pytest fixtures
│   ├── test_accounts.py
│   ├── test_events.py
│   ├── test_gamification.py
│   ├── test_security.py
│   └── test_social.py
│
├── 📄 docker-compose.yml     # Docker Compose (development)
├── 📄 docker-compose.prod.yml # Docker Compose (production)
├── 📄 Dockerfile             # Docker image (development)
├── 📄 Dockerfile.prod        # Docker image (production)
├── 📄 requirements.txt       # Python залежності
├── 📄 requirements-dev.txt   # Dev залежності
├── 📄 pyproject.toml         # Python project config
└── 📄 manage.py              # Django CLI
```

---

## 🔌 API Reference

### Аутентифікація

Всі API endpoints використовують JWT токени.

```bash
# Отримання токена
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'

# Відповідь
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Використання токена
curl -X GET http://localhost:8000/api/v1/auth/me/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Endpoints

| Endpoint | Метод | Опис | Auth |
|----------|-------|------|:----:|
| **Аутентифікація** ||||
| `/api/v1/auth/token/` | POST | Отримати JWT токен | ❌ |
| `/api/v1/auth/token/refresh/` | POST | Оновити access токен | ❌ |
| `/api/v1/auth/register/` | POST | Реєстрація нового користувача | ❌ |
| `/api/v1/auth/me/` | GET | Дані поточного користувача | ✅ |
| `/api/v1/auth/password/change/` | POST | Зміна пароля | ✅ |
| `/api/v1/auth/logout/` | POST | Logout (invalidate token) | ✅ |
| **Події** ||||
| `/events/api/events/search/` | GET | Пошук подій | ✅ |
| `/events/events/recommendations-preview/` | POST | Preview рекомендацій | ✅ |

---

## 🔐 Безпека

### Реалізовані заходи

| Захід | Статус | Опис |
|-------|:------:|------|
| **Password Hashing** | ✅ | Argon2id з високими параметрами |
| **JWT Authentication** | ✅ | Access (15 хв) + Refresh (7 днів) токени |
| **CSRF Protection** | ✅ | Django CSRF middleware |
| **XSS Protection** | ✅ | Auto-escaping + CSP headers |
| **Content Security Policy** | ✅ | Strict CSP з nonce для inline scripts |
| **Rate Limiting** | ✅ | Redis-based limiter для login/payment |
| **SQL Injection** | ✅ | Django ORM parameterized queries |
| **Captcha** | ✅ | Math-based captcha на реєстрації |
| **HTTPS Only** | ✅ | Redirect HTTP → HTTPS в production |
| **Security Headers** | ✅ | X-Frame-Options, X-Content-Type-Options |
| **Session Security** | ✅ | HttpOnly, Secure, SameSite cookies |
| **Input Validation** | ✅ | Django forms + manual validation |
| **Luhn Validation** | ✅ | Перевірка номерів карток |

### Рекомендації для Production

1. **Завжди використовуйте HTTPS** — налаштуйте SSL через Let's Encrypt або ваш провайдер
2. **Регулярно оновлюйте залежності** — `pip-audit` для перевірки вразливостей
3. **Використовуйте реальний платіжний шлюз** — Stripe, LiqPay, Fondy для оплат
4. **Налаштуйте моніторинг** — Sentry для помилок, Prometheus + Grafana для метрик
5. **Робіть регулярні бекапи** — використовуйте `scripts/backup.sh`

---

## 🧪 Тестування

### Запуск тестів

```bash
# Всі тести
docker exec alechemy_web python manage.py test

# Конкретний модуль
docker exec alechemy_web python manage.py test tests.test_accounts

# З pytest
docker exec alechemy_web pytest tests/ -v

# З покриттям
docker exec alechemy_web coverage run -m pytest tests/
docker exec alechemy_web coverage report -m
docker exec alechemy_web coverage html
```

### Структура тестів

```
tests/
├── conftest.py          # Fixtures (users, events, etc.)
├── test_accounts.py     # Реєстрація, логін, профіль
├── test_events.py       # CRUD подій, сценарії
├── test_gamification.py # Бали, досягнення
├── test_security.py     # Rate limiting, CSRF, XSS
└── test_social.py       # Друзі, запити
```

---

## 🌍 Локалізація

### Підтримувані мови

- 🇺🇦 **Українська** (основна)
- 🇬🇧 **English**

### Додавання перекладів

```bash
# Витягнути рядки для перекладу
docker exec alechemy_web python manage.py makemessages -l uk
docker exec alechemy_web python manage.py makemessages -l en

# Відредагуйте файли locale/*/LC_MESSAGES/django.po

# Скомпілювати переклади
docker exec alechemy_web python manage.py compilemessages
```

### Використання в шаблонах

```html
{% load i18n %}
<h1>{% trans "Привіт, світе!" %}</h1>
```

---

## 📊 Моніторинг

### Health Check

```bash
# Перевірка доступності
curl http://localhost:8000/health/
# Відповідь: {"status": "ok", "database": "ok", "cache": "ok"}
```

### Логи

```bash
# Всі контейнери
docker-compose logs -f

# Тільки web
docker-compose logs -f web

# Nginx access logs
docker exec alechemy_nginx tail -f /var/log/nginx/access.log
```

---

## 🤝 Внесок у проект

1. Fork репозиторію
2. Створіть feature branch: `git checkout -b feature/amazing-feature`
3. Commit зміни: `git commit -m 'Add amazing feature'`
4. Push в branch: `git push origin feature/amazing-feature`
5. Відкрийте Pull Request

### Стиль коду

- Python: PEP 8 + Black formatter
- JavaScript: ESLint
- HTML/CSS: Prettier

---

## 📄 Ліцензія

MIT License. Див. [LICENSE](LICENSE) для деталей.

---

## ⚠️ Disclaimer

**Цей застосунок надає приблизні розрахунки BAC (Blood Alcohol Content) виключно для інформаційних цілей.**

- Результати НЕ є медично точними
- НІКОЛИ не приймайте рішення про керування транспортом на основі цих даних
- Якщо ви вживали алкоголь — НЕ СІДАЙТЕ ЗА КЕРМО
- Зверніться до офіційних медичних джерел для точної інформації

---

<p align="center">
  Made with ❤️ by Alechemy Team
</p>
п