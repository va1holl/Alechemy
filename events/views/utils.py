"""
Utility functions and helpers for events views.
"""
from decimal import ROUND_HALF_UP, Decimal
import math

from django.db.models import Q
from django.http import Http404

from ..models import Event, EventParticipant, AlcoholLog


def _get_accessible_event_or_404(pk, user):
    """
    Безпечне отримання події - повертає 404 якщо подія не існує АБО користувач не має доступу.
    Запобігає ID enumeration attack.
    """
    event = Event.objects.filter(
        Q(pk=pk) & (
            Q(user=user) |
            Q(event_participants__participant=user, event_participants__status=EventParticipant.Status.ACCEPTED)
        )
    ).distinct().first()
    
    if event is None:
        raise Http404("Подію не знайдено")
    
    return event


def _get_admin_event_or_404(pk, user):
    """
    Безпечне отримання події для адмінів - 404 якщо подія не існує АБО користувач не адмін.
    """
    event = Event.objects.filter(
        Q(pk=pk) & (
            Q(user=user) |
            Q(event_participants__participant=user, 
              event_participants__status=EventParticipant.Status.ACCEPTED,
              event_participants__role=EventParticipant.Role.HEAD)
        )
    ).distinct().first()
    
    if event is None:
        raise Http404("Подію не знайдено")
    
    return event


def _get_owner_event_or_404(pk, user):
    """
    Безпечне отримання події для власника - 404 якщо подія не існує АБО користувач не власник.
    """
    event = Event.objects.filter(pk=pk, user=user).first()
    if event is None:
        raise Http404("Подію не знайдено")
    return event


def _can_access_event(event, user):
    """Перевіряє, чи може користувач дістатися до події (власник або прийнятий учасник)."""
    if event.user == user:
        return True
    return EventParticipant.objects.filter(
        event=event,
        participant=user,
        status=EventParticipant.Status.ACCEPTED
    ).exists()


def _is_event_admin(event, user):
    """Перевіряє, чи є користувач адміном події (власник або HEAD)."""
    if event.user == user:
        return True
    return EventParticipant.objects.filter(
        event=event,
        participant=user,
        status=EventParticipant.Status.ACCEPTED,
        role=EventParticipant.Role.HEAD
    ).exists()


def _get_user_role(event, user):
    """Отримує роль користувача у події."""
    if event.user == user:
        return "owner"
    participant = EventParticipant.objects.filter(
        event=event,
        participant=user,
        status=EventParticipant.Status.ACCEPTED
    ).first()
    if participant:
        return participant.role
    return None


def build_recommendations_placeholder(
    user,
    scenario,
    drink,
    dish,
    people_count=None,
    duration_hours=None,
):
    """
    Калькулятор рекомендацій для події.

    Розраховує:
    - орієнтовний об'єм напою на людину і загалом,
    - скільки це пляшок по 0.75л,
    - об'єм води,
    - приблизну кількість порцій їжі,
    - оцінку BAC на людину (за профілем користувача), якщо є дані.
    """
    profile = getattr(user, "profile", None)

    # --- вхідні параметри ---
    try:
        people = int(people_count) if people_count else 2
    except (TypeError, ValueError):
        people = 2

    try:
        hours = int(duration_hours) if duration_hours else 2
    except (TypeError, ValueError):
        hours = 2

    if people < 1:
        people = 1
    if hours < 1:
        hours = 1

    # --- розрахунок алкоголю ---
    base_serving_volume_ml = 150  # "порція" для вина/лонгдрінка
    servings_per_person = max(1.0, float(hours))  # 1 порція на годину
    per_person_alcohol_ml = int(servings_per_person * base_serving_volume_ml)
    total_alcohol_ml = per_person_alcohol_ml * people
    bottles_750_ml = max(1, math.ceil(total_alcohol_ml / 750))

    # --- вода ---
    per_person_water_ml = max(500, int(hours * 300))
    total_water_ml = per_person_water_ml * people
    water_bottles_1500_ml = max(1, math.ceil(total_water_ml / 1500))

    # --- їжа ---
    food_factor = 1.5
    food_portions = max(1, math.ceil(people * food_factor))

    summary = (
        f"📊 Розрахунок на {people} {'людину' if people == 1 else 'людей'} при тривалості {hours} год: "
        f"≈{per_person_alcohol_ml} мл напою на людину "
        f"(всього ~{total_alcohol_ml} мл, це близько {bottles_750_ml} пляшок по 0.75 л). "
        f"💧 Води потрібно мінімум {per_person_water_ml} мл на людину "
        f"(всього ~{total_water_ml} мл, ≈{water_bottles_1500_ml} пляшок по 1.5 л). "
        f"🍽️ Їжі орієнтовно на {food_portions} порцій."
    )

    bac_promille = None

    if profile and drink and getattr(drink, "abv", None):
        dummy_log = AlcoholLog(
            user=user,
            drink=drink,
            volume_ml=per_person_alcohol_ml,
            abv=drink.abv,
        )
        bac_promille = dummy_log.calculate_bac()

        if bac_promille is not None:
            summary += (
                f" 🍺 Для вас це може дати близько {bac_promille} ‰ BAC "
                f"(орієнтовно, не використовувати для рішень про керування авто)."
            )
        else:
            summary += " ℹ️ Для оцінки BAC заповніть вагу та стать у профілі."
    elif profile:
        summary += " ℹ️ Для розрахунку BAC потрібен напій з вказаною міцністю та заповнені дані профілю."

    return {
        "summary": summary,
        "people": people,
        "hours": hours,
        "per_person_alcohol_ml": per_person_alcohol_ml,
        "total_alcohol_ml": total_alcohol_ml,
        "bottles_750_ml": bottles_750_ml,
        "per_person_water_ml": per_person_water_ml,
        "total_water_ml": total_water_ml,
        "water_bottles_1500_ml": water_bottles_1500_ml,
        "food_portions": food_portions,
        "bac_promille": bac_promille,
    }


def build_recovery_advice(user, drink, recommendations):
    """
    Поради щодо відновлення після вживання алкоголю.
    Використовуємо оцінковий BAC та стандартну швидкість виведення.
    """
    if not recommendations:
        return None

    bac = recommendations.get("bac_promille")
    if not bac:
        return None

    if not isinstance(bac, Decimal):
        bac = Decimal(str(bac))

    elimination_rate = Decimal("0.15")
    hours_to_zero = (bac / elimination_rate).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    per_person_water_ml = recommendations.get("per_person_water_ml") or 0
    try:
        per_person_water_ml = int(per_person_water_ml)
    except (TypeError, ValueError):
        per_person_water_ml = 0

    extra_water_ml = max(0, int(per_person_water_ml * 0.5))

    text = (
        f"🌙 **Стадія відновлення**\n\n"
        f"При такому об'ємі напою орієнтовний пік для вас — близько {bac} ‰. "
        f"Організм в середньому виводить приблизно 0.15 ‰ алкоголю на годину, тому до майже повного "
        f"протверезіння може пройти близько **{hours_to_zero} год**.\n\n"
    )

    if extra_water_ml > 0:
        text += (
            f"💧 **Рекомендації:**\n"
            f"• Випийте ще хоча б {extra_water_ml} мл води понад те, що планувалося під час вечора\n"
            f"• Нормально поїжте\n"
            f"• Відпочиньте та виспіться"
        )
    else:
        text += "💧 Після події варто переключитись на воду та нормальну їжу."

    text += (
        "\n\n⚠️ _Ця оцінка дуже орієнтовна і не підходить для рішень щодо керування авто, "
        "здоров'я або дозування ліків._"
    )

    return text
