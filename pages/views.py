import json
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta
from functools import wraps

from accounts.models import Profile, Notification
from accounts.rate_limit import rate_limit
from events.views import get_diary_stats_for_user
from .forms import ProfileForm


# Premium decorator
def premium_required(view_func):
    """Декоратор для функцій, що потребують Premium."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if not profile.is_premium:
            return redirect('pages:plan_choice')
        return view_func(request, *args, **kwargs)
    return wrapper


class HomeView(TemplateView):
    template_name = "pages/home.html"


@login_required
def dashboard_view(request):
    """Dashboard for authenticated users."""
    from events.models import Event, EventParticipant
    from django.db.models import Q
    
    profile, _ = Profile.objects.get_or_create(user=request.user)
    today = timezone.now()
    
    # Get user's upcoming events (own + where participant, only active)
    events = (
        Event.objects.filter(
            Q(user=request.user) |
            Q(
                event_participants__participant=request.user,
                event_participants__status=EventParticipant.Status.ACCEPTED
            )
        )
        .filter(is_finished=False)
        .select_related('scenario', 'drink', 'dish')
        .distinct()
        .order_by('date')[:4]
    )
    # Count only active events (own + participant)
    events_count = Event.objects.filter(
        Q(user=request.user) |
        Q(
            event_participants__participant=request.user,
            event_participants__status=EventParticipant.Status.ACCEPTED
        )
    ).filter(is_finished=False).distinct().count()
    
    return render(request, "pages/dashboard.html", {
        "profile": profile,
        "events": events,
        "events_count": events_count,
        "today": today,
    })


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(instance=profile)
        diary_stats = get_diary_stats_for_user(request.user)
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()

        return render(
            request,
            "pages/profile.html",
            {
                "profile": profile,
                "form": form,
                "diary_stats": diary_stats,
                "unread_notifications": unread_notifications,
            },
        )

    def post(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("pages:me")

        diary_stats = get_diary_stats_for_user(request.user)

        return render(
            request,
            "pages/profile.html",
            {
                "profile": profile,
                "form": form,
                "diary_stats": diary_stats,
            },
        )


@login_required
def personal_data_view(request):
    """Сторінка персональних даних з валідацією."""
    from django.contrib import messages
    from django.core.exceptions import ValidationError
    import re
    
    profile, _ = Profile.objects.get_or_create(user=request.user)
    errors = []
    
    if request.method == "POST":
        # Валідація та очистка даних
        weight_raw = request.POST.get("weight", "").strip()
        height_raw = request.POST.get("height", "").strip()
        sex = request.POST.get("sex", "").strip()
        display_name = request.POST.get("display_name", "").strip()
        # is_adult_confirmed та gdpr_consent встановлюються при реєстрації і не змінюються тут
        
        # Зберігаємо display_name (до 50 символів)
        profile.display_name = display_name[:50] if display_name else ""
        
        # Валідація ваги (30-300 кг)
        if weight_raw:
            try:
                weight = float(weight_raw)
                if weight < 30 or weight > 300:
                    errors.append("Вага має бути від 30 до 300 кг")
                else:
                    profile.weight_kg = weight
            except (ValueError, TypeError):
                errors.append("Невірний формат ваги")
        
        # Валідація зросту (100-250 см)
        if height_raw:
            try:
                height = int(height_raw)
                if height < 100 or height > 250:
                    errors.append("Зріст має бути від 100 до 250 см")
                else:
                    profile.height_cm = height
            except (ValueError, TypeError):
                errors.append("Невірний формат зросту")
        
        # Валідація дати народження (18+)
        birth_date_raw = request.POST.get("birth_date", "").strip()
        if birth_date_raw:
            try:
                from datetime import date, datetime
                bd = datetime.strptime(birth_date_raw, "%Y-%m-%d").date()
                today = date.today()
                age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
                if bd > today:
                    errors.append("Дата народження не може бути в майбутньому")
                elif age < 18:
                    errors.append("Вам має бути 18 років або більше")
                elif age > 120:
                    errors.append("Невірна дата народження")
                else:
                    profile.birth_date = bd
            except (ValueError, TypeError):
                errors.append("Невірний формат дати народження")
        
        # Валідація статі (тільки дозволені значення)
        if sex:
            allowed_sex = [choice[0] for choice in Profile.Sex.choices]
            if sex in allowed_sex:
                profile.sex = sex
            else:
                errors.append("Невірне значення статі")
        

        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            profile.save()
            messages.success(request, "Дані успішно збережено!")
            return redirect("pages:personal_data")
    
    from datetime import date
    today = date.today()
    max_birth_date = today.replace(year=today.year - 18)
    return render(request, "pages/personal_data.html", {"profile": profile, "max_birth_date": max_birth_date})


@login_required
def notifications_view(request):
    """Сторінка сповіщень з групуванням за датами."""
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    
    # Позначаємо всі непрочитані як прочитані
    unread = notifications.filter(is_read=False)
    unread.update(is_read=True)
    
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Групуємо сповіщення за датами
    today_notifications = []
    yesterday_notifications = []
    older_notifications = {}
    
    for n in notifications:
        n_date = n.created_at.date()
        if n_date == today:
            today_notifications.append(n)
        elif n_date == yesterday:
            yesterday_notifications.append(n)
        else:
            date_key = n_date.strftime("%d %B")
            if date_key not in older_notifications:
                older_notifications[date_key] = []
            older_notifications[date_key].append(n)
    
    return render(request, "pages/notifications.html", {
        "today_notifications": today_notifications,
        "yesterday_notifications": yesterday_notifications,
        "older_notifications": older_notifications,
    })


@login_required
def notification_action(request, notification_id, action):
    """Прийняти або відхилити сповіщення."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    if action == "accept":
        notification.respond("accept")
        # Тут можна додати логіку для різних типів (прийняти запит у друзі і т.д.)
        if notification.notification_type == "friend_request" and notification.related_user:
            from accounts.models import FriendRequest
            try:
                fr = FriendRequest.objects.get(from_user=notification.related_user, to_user=request.user)
                fr.accept()
            except FriendRequest.DoesNotExist:
                pass
        elif notification.notification_type == "event_invite" and notification.related_event:
            from events.models import EventParticipant
            try:
                ep = EventParticipant.objects.get(event=notification.related_event, participant=request.user)
                ep.accept()
            except EventParticipant.DoesNotExist:
                pass
    elif action == "decline":
        notification.respond("decline")
        if notification.notification_type == "friend_request" and notification.related_user:
            from accounts.models import FriendRequest
            try:
                fr = FriendRequest.objects.get(from_user=notification.related_user, to_user=request.user)
                fr.reject()
            except FriendRequest.DoesNotExist:
                pass
        elif notification.notification_type == "event_invite" and notification.related_event:
            from events.models import EventParticipant
            try:
                ep = EventParticipant.objects.get(event=notification.related_event, participant=request.user)
                ep.decline()
            except EventParticipant.DoesNotExist:
                pass
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "ok"})
    return redirect("pages:notifications")


@login_required
def calculator_view(request):
    """BAC калькулятор."""
    from recipes.models import Cocktail
    
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # Значення за замовчуванням з профілю
    default_weight = profile.weight_kg or 70
    default_height = profile.height_cm or 180
    default_gender = "male" if profile.sex == "m" else "female"
    
    # Список коктейлів для пошуку (тільки name і slug)
    cocktails = Cocktail.objects.filter(is_active=True).values('name', 'slug').order_by('name')
    cocktails_list = list(cocktails)
    
    return render(request, "pages/calculator.html", {
        "profile": profile,
        "default_weight": default_weight,
        "default_height": default_height,
        "default_gender": default_gender,
        "cocktails_json": json.dumps(cocktails_list, cls=DjangoJSONEncoder),
    })


# ============== PREMIUM VIEWS ==============

@login_required
def plan_choice_view(request):
    """Сторінка вибору плану Free/Premium."""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "pages/premium/plan_choice.html", {
        "profile": profile,
    })


@login_required
@rate_limit('payment', limit=3, period=60, block_time=600)
def payment_form_view(request):
    """Форма оплати Premium."""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    if profile.is_premium:
        return redirect('pages:plan_choice')
    
    trial = request.GET.get('trial', '0') == '1'
    
    if request.method == 'POST':
        import re
        import logging
        logger = logging.getLogger('django.security')
        
        # Отримуємо та очищаємо дані
        card_number = re.sub(r'\D', '', request.POST.get('card_number', ''))
        cvv = re.sub(r'\D', '', request.POST.get('cvv', ''))
        expiry = request.POST.get('expiry', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        is_trial = request.POST.get('trial', '0') == '1'
        
        errors = []
        
        # Валідація імені (тільки літери та пробіли)
        if len(full_name) < 3:
            errors.append("Ім'я занадто коротке")
        elif not re.match(r'^[a-zA-Zа-яА-ЯіІїЇєЄґҐ\s\-\']+$', full_name):
            errors.append("Ім'я містить недопустимі символи")
        
        # Валідація номера картки (16 цифр)
        if len(card_number) != 16:
            errors.append("Номер картки має містити 16 цифр")
        # DEMO MODE: приймаємо будь-які 16 цифр без Luhn перевірки
        # В production потрібно розкоментувати Luhn validation або підключити платіжний шлюз
        
        # ПРИМІТКА: В production потрібно підключити реальний платіжний шлюз (Stripe, LiqPay тощо)
        
        # Валідація CVV (будь-які 3 цифри для demo)
        if len(cvv) != 3:
            errors.append("CVV має містити 3 цифри")
        
        # Валідація терміну дії
        expiry_match = re.match(r'^(\d{2})\s*/\s*(\d{2})$', expiry)
        if not expiry_match:
            errors.append("Невірний формат терміну дії (MM / YY)")
        else:
            try:
                month = int(expiry_match.group(1))
                year = int('20' + expiry_match.group(2))
                if month < 1 or month > 12:
                    errors.append("Невірний місяць")
                from datetime import date
                if date(year, month, 1) < date.today().replace(day=1):
                    errors.append("Картка прострочена")
            except (ValueError, TypeError):
                errors.append("Невірний формат терміну дії")
        
        if errors:
            # Логуємо невдалі спроби оплати
            logger.warning(f"Payment validation failed for user {request.user.id}: {errors}")
            return render(request, "pages/premium/payment_form.html", {
                "profile": profile,
                "trial": is_trial,
                "errors": errors,
            })
        
        # Логуємо успішну активацію (без карткових даних!)
        logger.info(f"Premium activated for user {request.user.id}")
        
        # Активуємо Premium
        profile.is_premium = True
        if is_trial:
            profile.premium_trial_end = timezone.now() + timedelta(days=3)
        profile.save()
        
        # Створюємо сповіщення
        Notification.objects.create(
            user=request.user,
            notification_type='system',
            title='Premium активовано!',
            message='Вітаємо! Тепер вам доступні всі преміум-функції Alechemy.',
        )
        
        return redirect('pages:payment_success')
    
    return render(request, "pages/premium/payment_form.html", {
        "profile": profile,
        "trial": trial,
    })


@login_required
def payment_success_view(request):
    """Сторінка успішної оплати."""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "pages/premium/payment_success.html", {
        "profile": profile,
    })


@login_required
@rate_limit('delete_account', limit=3, period=300, block_time=900)
def delete_account_view(request):
    """Видалення акаунту з підтвердженням паролем."""
    from django.contrib.auth import logout, authenticate
    from django.contrib import messages
    import logging
    
    logger = logging.getLogger('django.security')
    error = None
    
    if request.method == "POST":
        password = request.POST.get("password", "")
        confirm_text = request.POST.get("confirm_text", "").strip().lower()
        
        # Перевірка введення "видалити"
        if confirm_text != "видалити":
            error = "Введіть 'видалити' для підтвердження"
        # Перевірка пароля
        elif not password:
            error = "Введіть пароль"
        else:
            user = authenticate(username=request.user.email, password=password)
            if user is None:
                error = "Невірний пароль"
                logger.warning(f"Failed delete account attempt for user {request.user.id}")
            else:
                # Успішне видалення
                logger.info(f"Account deleted: user_id={request.user.id}, email={request.user.email}")
                user_to_delete = request.user
                logout(request)
                user_to_delete.delete()
                messages.success(request, "Ваш акаунт успішно видалено.")
                return redirect("pages:home")
    
    return render(request, "pages/delete_account.html", {"error": error})


def privacy_policy_view(request):
    """Сторінка політики конфіденційності."""
    return render(request, "pages/privacy_policy.html")


@login_required
def settings_view(request):
    """Сторінка налаштувань користувача."""
    from django.conf import settings as django_settings
    
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        # Handle settings updates
        action = request.POST.get("action")
        
        if action == "notifications":
            profile.notifications_enabled = request.POST.get("notifications_enabled") == "on"
            profile.email_notifications = request.POST.get("email_notifications") == "on"
            profile.push_notifications = request.POST.get("push_notifications") == "on"
            profile.save()
        
        elif action == "privacy":
            profile.profile_visible = request.POST.get("profile_visible") == "on"
            profile.show_in_leaderboard = request.POST.get("show_in_leaderboard") == "on"
            profile.save()
        
        elif action == "theme":
            profile.theme = request.POST.get("theme", "dark")
            profile.save()
        
        return redirect("pages:settings")
    
    # Available languages
    languages = [
        {"code": "uk", "name": "Українська", "flag": "🇺🇦"},
        {"code": "en", "name": "English", "flag": "🇬🇧"},
        {"code": "ru", "name": "Російська", "flag": "🇷🇺"},
    ]
    
    current_language = request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else 'uk'
    
    return render(request, "pages/settings.html", {
        "profile": profile,
        "languages": languages,
        "current_language": current_language,
    })


def set_language_view(request):
    """Зміна мови інтерфейсу."""
    from django.utils import translation
    from django.conf import settings as django_settings
    from django.http import HttpResponseRedirect
    from django.utils.http import url_has_allowed_host_and_scheme
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == "POST":
        language = request.POST.get("language", "uk")
        logger.info(f"set_language_view: language={language}")
        
        # Якщо обрано російську - редірект на ab3.army
        if language == "ru":
            logger.info("Redirecting to ab3.army")
            return HttpResponseRedirect("https://ab3.army/")
        
        # Validate language code
        valid_codes = [lang[0] for lang in getattr(django_settings, 'LANGUAGES', [('uk', 'Ukrainian'), ('en', 'English')])]
        if language not in valid_codes:
            language = "uk"
        
        # Set language
        translation.activate(language)
        
        # Validate next URL to prevent Open Redirect
        next_url = request.POST.get("next", "")
        if not next_url or not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure()
        ):
            next_url = "pages:settings"
        
        response = redirect(next_url)
        response.set_cookie(
            django_settings.LANGUAGE_COOKIE_NAME,
            language,
            max_age=365 * 24 * 60 * 60,  # 1 year
            samesite='Lax',
        )
        
        # Save to profile if authenticated
        if request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            profile.language = language
            profile.save(update_fields=['language'])
        
        return response
    
    return redirect("pages:settings")


def custom_404(request, exception):
    return render(request, "404.html", status=404)


def custom_500(request):
    return render(request, "500.html", status=500)