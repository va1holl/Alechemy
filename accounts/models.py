from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import date
import uuid
import random
import string


def generate_unique_tag():
    """Генерує унікальний тег для користувача типу #ABC123"""
    chars = string.ascii_uppercase + string.digits
    return '#' + ''.join(random.choices(chars, k=6))


class User(AbstractUser):
    """
    Кастомный пользователь: логинимся по email, он уникальный.
    """
    email = models.EmailField(_("email address"), unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email or self.username


class Profile(models.Model):
    class Sex(models.TextChoices):
        MALE = "m", "Мужской"
        FEMALE = "f", "Женский"
        OTHER = "other", "Другое / не указано"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    # Унікальний тег для пошуку друзів (наприклад #ABC123) - генерується автоматично
    unique_tag = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        help_text="Унікальний тег для запрошення друзів (наприклад #ABC123)"
    )
    
    # Відображуване ім'я - показується у коментарях, чатах тощо
    display_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ім'я, яке бачитимуть інші користувачі"
    )

    # по ТЗ: дата народження, стать, вага, зріст
    birth_date = models.DateField(null=True, blank=True, help_text="Дата народження")

    @property
    def age(self):
        """Вік розраховується автоматично з дати народження."""
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    sex = models.CharField(
        max_length=10,
        choices=Sex.choices,
        blank=True,
        help_text="Нужно для более точной оценки BAC",
    )
    height_cm = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Рост в см",
    )
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Вес в кг, нужен для BAC",
    )

    is_adult_confirmed = models.BooleanField(
        default=False,
        help_text="Подтверждение, что пользователю 18+.",
    )
    gdpr_consent = models.BooleanField(
        default=False,
        help_text="Согласие на обработку персональных данных.",
    )

    favorite_scenarios = models.ManyToManyField(
        "events.Scenario",
        related_name="favorite_for_profiles",
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
    )

    is_premium = models.BooleanField(default=False)
    premium_trial_end = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Дата закінчення пробного періоду Premium"
    )

    # Settings fields
    language = models.CharField(
        max_length=5,
        default='uk',
        choices=[('uk', 'Українська'), ('en', 'English')],
        help_text="Мова інтерфейсу"
    )
    theme = models.CharField(
        max_length=10,
        default='dark',
        choices=[('dark', 'Темна'), ('light', 'Світла'), ('auto', 'Авто')],
        help_text="Тема інтерфейсу"
    )
    notifications_enabled = models.BooleanField(
        default=True,
        help_text="Загальні сповіщення"
    )
    email_notifications = models.BooleanField(
        default=True,
        help_text="Email сповіщення"
    )
    push_notifications = models.BooleanField(
        default=True,
        help_text="Push сповіщення"
    )
    profile_visible = models.BooleanField(
        default=True,
        help_text="Профіль видимий для інших"
    )
    show_in_leaderboard = models.BooleanField(
        default=True,
        help_text="Показувати у таблиці лідерів"
    )

    def save(self, *args, **kwargs):
        # Генеруємо унікальний тег при створенні профілю
        if not self.unique_tag:
            for _ in range(10):  # 10 спроб знайти унікальний
                tag = generate_unique_tag()
                if not Profile.objects.filter(unique_tag=tag).exists():
                    self.unique_tag = tag
                    break
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Профиль {self.user.email or self.user.username}"
    
    def get_display_name(self):
        """Отримати ім'я для відображення у коментарях, чатах тощо."""
        if self.display_name:
            return self.display_name
        if self.user.first_name:
            return self.user.first_name
        if self.unique_tag:
            return self.unique_tag
        return self.user.username or "Користувач"

    def get_friends(self):
        """Получить список принятых друзей (в обе стороны)"""
        return User.objects.filter(
            models.Q(
                id__in=self.user.sent_friend_requests.filter(
                    status='accepted'
                ).values_list('to_user_id', flat=True)
            ) | models.Q(
                id__in=self.user.received_friend_requests.filter(
                    status='accepted'
                ).values_list('from_user_id', flat=True)
            )
        )

    def get_pending_requests(self):
        """Получить список ожидающих входящих запросов в друзья"""
        return self.user.received_friend_requests.filter(status='pending')

    def get_friend_event_count(self, friend):
        """Получить количество совместных событий с другом"""
        from events.models import Event
        return Event.objects.filter(
            user=self.user, event_participants__participant=friend
        ).count() + Event.objects.filter(
            user=friend, event_participants__participant=self.user
        ).count()


class FriendRequest(models.Model):
    """
    Модель для запроса в друзья.
    from_user отправляет запрос к to_user.
    """
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидание"
        ACCEPTED = "accepted", "Принято"
        REJECTED = "rejected", "Отклонено"
        BLOCKED = "blocked", "Заблокировано"

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests"
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_friend_requests"
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("from_user", "to_user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.from_user.email} → {self.to_user.email} ({self.status})"

    def accept(self):
        """Принять запрос в друзья"""
        self.status = self.Status.ACCEPTED
        self.save()

    def reject(self):
        """Отклонить запрос в друзья"""
        self.status = self.Status.REJECTED
        self.save()


class Notification(models.Model):
    """
    Система сповіщень для користувачів.
    """
    class NotificationType(models.TextChoices):
        FRIEND_REQUEST = "friend_request", "Запит у друзі"
        EVENT_INVITE = "event_invite", "Запрошення на подію"
        ACHIEVEMENT = "achievement", "Досягнення"
        CHALLENGE = "challenge", "Челендж"
        SYSTEM = "system", "Системне"
    
    class ResponseAction(models.TextChoices):
        NONE = "none", "Без відповіді"
        ACCEPTED = "accepted", "Прийнято"
        DECLINED = "declined", "Відхилено"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    
    # Для запитів, що потребують дії
    action_required = models.BooleanField(default=False)
    action_url = models.CharField(max_length=255, blank=True)
    related_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_notifications"
    )
    related_event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )
    
    # Відповідь користувача
    response_action = models.CharField(
        max_length=10,
        choices=ResponseAction.choices,
        default=ResponseAction.NONE
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email}: {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    def respond(self, action):
        """Відповісти на сповіщення (accept/decline)."""
        from django.utils import timezone
        if action == "accept":
            self.response_action = self.ResponseAction.ACCEPTED
        elif action == "decline":
            self.response_action = self.ResponseAction.DECLINED
        self.responded_at = timezone.now()
        self.is_read = True
        self.save()