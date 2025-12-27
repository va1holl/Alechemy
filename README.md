# 🍸 Alechemy

**Розумний помічник для планування вечірок з алкоголем**

Alechemy — це веб-застосунок, який допомагає планувати події, розраховувати кількість напоїв та їжі, відстежувати споживання алкоголю та підтримувати соціальні зв'язки з друзями.

## ✨ Функціональність

- 📅 **Планування подій** — створення подій з вибором сценарію, напоїв та страв
- 🛒 **Розрахунок покупок** — автоматичний підрахунок кількості продуктів на основі кількості гостей
- 📊 **Алко-щоденник** — відстеження споживання з приблизною оцінкою BAC
- 🏆 **Гейміфікація** — бали, досягнення та челенджі
- 👥 **Соціальні функції** — друзі, рейтинги, спільні події
- 📈 **Статистика** — PDF-звіти, графіки та аналітика

## 🛠 Технології

- **Backend:** Django 5.2, Django REST Framework
- **Database:** PostgreSQL 16
- **Cache:** Redis 7
- **Server:** Gunicorn + Nginx
- **Auth:** JWT, 2FA (TOTP), hCaptcha
- **Container:** Docker, Docker Compose

## 🚀 Швидкий старт (Development)

### Вимоги
- Docker & Docker Compose
- Python 3.12+ (для локальної розробки)

### Запуск

1. **Клонуйте репозиторій:**
   ```bash
   git clone https://github.com/your-username/alechemy.git
   cd alechemy
   ```

2. **Створіть файл `.env`:**
   ```bash
   cp .env.example .env
   # Відредагуйте .env за потреби
   ```

3. **Запустіть Docker:**
   ```bash
   docker-compose up -d
   ```

4. **Застосуйте міграції:**
   ```bash
   docker exec alechemy_web python manage.py migrate
   ```

5. **Створіть суперкористувача:**
   ```bash
   docker exec -it alechemy_web python manage.py createsuperuser
   ```

6. **Відкрийте у браузері:**
   - Застосунок: http://localhost:8000
   - Адмінка: http://localhost:8000/admin/

## 🏭 Production Deployment

### Налаштування

1. **Створіть production файл оточення:**
   ```bash
   cp .env.prod.example .env.prod
   # Заповніть реальними значеннями
   ```

2. **Згенеруйте SECRET_KEY:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Налаштуйте SSL сертифікати:**
   ```bash
   # Покладіть сертифікати в nginx/ssl/
   # fullchain.pem - сертифікат
   # privkey.pem - приватний ключ
   ```

### Запуск Production

```bash
# Збірка та запуск
docker-compose -f docker-compose.prod.yml up -d --build

# Застосування міграцій
docker exec alechemy_web python manage.py migrate

# Створення суперкористувача
docker exec -it alechemy_web python manage.py createsuperuser
```

### Корисні команди

```bash
# Перегляд логів
docker-compose -f docker-compose.prod.yml logs -f web

# Перезапуск
docker-compose -f docker-compose.prod.yml restart web

# Бекап бази даних
docker exec alechemy_db pg_dump -U $DB_USER $DB_NAME > backup.sql

# Відновлення з бекапу
docker exec -i alechemy_db psql -U $DB_USER $DB_NAME < backup.sql
```

## 📁 Структура проекту

```
alechemy/
├── accounts/          # Користувачі, авторизація, профілі
├── alechemy/          # Налаштування Django проекту
├── events/            # Події, сценарії, напої, страви
├── gamification/      # Бали, досягнення, челенджі
├── health/            # Health check endpoint
├── nginx/             # Конфігурація Nginx
├── pages/             # Основні сторінки (дашборд, налаштування)
├── places/            # Локації та магазини
├── recipes/           # Рецепти коктейлів
├── shopping/          # Розрахунок списку покупок
├── social/            # Друзі, рейтинги
├── static/            # Статичні файли (CSS, JS, images)
├── stats/             # Статистика та звіти
├── templates/         # HTML шаблони
└── locale/            # Переклади (uk, en)
```

## 🔐 Безпека

- ✅ Argon2 хешування паролів
- ✅ JWT токени для API
- ✅ 2FA (TOTP) для адмінки
- ✅ hCaptcha для реєстрації
- ✅ CSRF/XSS захист
- ✅ Content Security Policy
- ✅ Rate limiting
- ✅ HTTPS only (production)
- ✅ Security headers

## 🌍 Локалізація

Підтримувані мови:
- 🇺🇦 Українська (основна)
- 🇬🇧 English

## 📝 API

REST API доступний за адресою `/api/v1/`:

| Endpoint | Метод | Опис |
|----------|-------|------|
| `/api/v1/auth/token/` | POST | Отримати JWT токен |
| `/api/v1/auth/token/refresh/` | POST | Оновити токен |
| `/api/v1/auth/register/` | POST | Реєстрація |
| `/api/v1/auth/me/` | GET | Поточний користувач |

## 🧪 Тестування

```bash
# Запуск тестів
docker exec alechemy_web python manage.py test

# З покриттям
docker exec alechemy_web coverage run manage.py test
docker exec alechemy_web coverage report
```

## 📄 Ліцензія

MIT License. Див. [LICENSE](LICENSE) для деталей.

## 👨‍💻 Розробники

- Alechemy Team

---

**⚠️ Важливо:** Цей застосунок надає приблизні розрахунки BAC тільки для інформаційних цілей. Ніколи не приймайте рішення про водіння чи інші небезпечні дії на основі цих даних.
