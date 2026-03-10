"""
Event CRUD views - list, create, edit, delete, detail.
"""
import logging

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _

from accounts.decorators import adult_required
from ..models import Scenario, Event, Dish, Drink, EventParticipant, EventMessage
from ..forms import EventCreateFromScenarioForm, EventUpdateForm
from .utils import (
    _get_accessible_event_or_404,
    build_recommendations_placeholder,
    build_recovery_advice,
)

logger = logging.getLogger(__name__)


@login_required
@adult_required
def event_list(request):
    """Список подій користувача (власні та де учасник)."""
    all_events = Event.objects.filter(
        Q(user=request.user) |
        Q(
            event_participants__participant=request.user,
            event_participants__status=EventParticipant.Status.ACCEPTED
        )
    ).select_related("scenario", "drink", "dish").distinct().order_by("-date", "-created_at")
    
    # Розділяємо активні події та архів (завершені)
    show_archive = request.GET.get('archive') == '1'
    
    if show_archive:
        events = all_events.filter(is_finished=True)
    else:
        events = all_events.filter(is_finished=False)
    
    # Кількість в архіві для бейджа
    archive_count = all_events.filter(is_finished=True).count()
    
    # ID власних подій для відображення бейджа "Учасник"
    own_event_ids = set(Event.objects.filter(user=request.user).values_list('id', flat=True))
    
    return render(request, "events/event_list.html", {
        "events": events,
        "own_event_ids": own_event_ids,
        "show_archive": show_archive,
        "archive_count": archive_count,
    })


@login_required
@adult_required
def event_create_from_scenario(request, slug):
    """Створення події на основі сценарію."""
    scenario = get_object_or_404(Scenario, slug=slug)

    if request.method == "POST":
        step = request.POST.get("step", "select_dish")
        drink_ids = request.POST.getlist("drink_ids")
        drink_id = request.POST.get("drink_id") or (drink_ids[0] if drink_ids else None)
        dish_ids = request.POST.getlist("dish_ids")
        dish_id = request.POST.get("dish_id") or (dish_ids[0] if dish_ids else None)
        difficulty = request.POST.get("difficulty") or ""

        drink = get_object_or_404(Drink, id=drink_id) if drink_id else None
        # Збираємо всі вибрані страви (множинний вибір)
        all_dish_ids = dish_ids if dish_ids else ([dish_id] if dish_id else [])
        dishes_qs = Dish.objects.filter(id__in=all_dish_ids) if all_dish_ids else Dish.objects.none()
        dishes = list(dishes_qs)
        # Збираємо всі вибрані напої
        all_drink_ids = drink_ids if drink_ids else ([drink_id] if drink_id else [])
        drinks_list = list(Drink.objects.filter(id__in=all_drink_ids)) if all_drink_ids else []

        if step == "select_dish":
            # Pre-fill form with values from scenario page
            initial_data = {
                'people_count': request.POST.get('people_count') or 2,
                'duration_hours': request.POST.get('duration_hours') or 3,
            }
            intensity = request.POST.get('intensity') or 'medium'
            form = EventCreateFromScenarioForm(initial=initial_data)
            recommendations = build_recommendations_placeholder(
                request.user, scenario, drink, dishes[0] if dishes else None,
                people_count=request.POST.get('people_count'),
                duration_hours=request.POST.get('duration_hours'),
            )
            return render(
                request,
                "events/event_create.html",
                {
                    "scenario": scenario,
                    "drink": drink,
                    "dish": dishes[0] if dishes else None,
                    "dishes": dishes,
                    "difficulty": difficulty,
                    "form": form,
                    "recommendations": recommendations,
                    "people_count_readonly": True,
                    "intensity": intensity,
                },
            )

        form = EventCreateFromScenarioForm(request.POST)
        intensity = request.POST.get('intensity') or 'medium'
        if form.is_valid() and drink:
            event = form.save(commit=False)
            event.user = request.user
            event.scenario = scenario
            event.drink = drink
            event.dish = dishes[0] if dishes else None
            event.intensity = intensity
            event.save()

            # Зберігаємо M2M зв'язки
            if drinks_list:
                event.drinks.set(drinks_list)
            if dishes:
                event.dishes.set(dishes)

            # Нараховуємо бали за створення події
            from gamification.services import award_points
            award_points(request.user, 'event_create')
            
            return redirect("events:event_list")
        else:
            logger.warning(f"Event creation failed: form.errors={form.errors}, drink={drink}, drink_id={drink_id}")

        recommendations = build_recommendations_placeholder(
            request.user,
            scenario,
            drink,
            dishes[0] if dishes else None,
            people_count=request.POST.get("people_count"),
            duration_hours=request.POST.get("duration_hours"),
        )
        return render(
            request,
            "events/event_create.html",
            {
                "scenario": scenario,
                "drink": drink,
                "dish": dishes[0] if dishes else None,
                "dishes": dishes,
                "difficulty": difficulty,
                "form": form,
                "recommendations": recommendations,
                "people_count_readonly": True,
                "intensity": intensity,
            },
        )

    return redirect("events:scenario_detail", slug=slug)


@login_required
@adult_required
def event_edit(request, pk):
    """Редагування події."""
    event = get_object_or_404(Event, pk=pk, user=request.user)
    
    # Запобігти редагуванню завершених подій
    if event.is_finished:
        messages.warning(request, _("Ви не можете редагувати завершену подію. Переглядайте її деталі або залишьте відгук."))
        return redirect("events:event_detail", pk=pk)
    
    scenario = event.scenario

    if request.method == "POST":
        form = EventUpdateForm(request.POST, instance=event, scenario=scenario)
        if form.is_valid():
            event = form.save()
            return redirect("events:event_detail", pk=event.pk)
    else:
        form = EventUpdateForm(instance=event, scenario=scenario)

    recommendations = build_recommendations_placeholder(
        request.user,
        scenario,
        form.instance.drink,
        form.instance.dish,
        people_count=form.instance.people_count,
        duration_hours=form.instance.duration_hours,
    )

    # Рекомендовані страви на основі напоїв сценарію
    all_dishes = Dish.objects.all().order_by("name")
    recommended_dish_ids = set()
    if scenario:
        recommended_dish_ids = set(
            Dish.objects.filter(drinks__in=scenario.drinks.all())
            .distinct()
            .values_list("id", flat=True)
        )

    return render(
        request,
        "events/event_edit.html",
        {
            "event": event,
            "scenario": scenario,
            "form": form,
            "recommendations": recommendations,
            "all_dishes": all_dishes,
            "recommended_dish_ids": recommended_dish_ids,
        },
    )


@require_POST
@login_required
@adult_required
def event_delete(request, pk):
    """Видалення події."""
    event = get_object_or_404(Event, pk=pk, user=request.user)
    event.delete()
    return redirect("events:event_deleted")


@login_required
@adult_required
def event_detail(request, pk):
    """Деталі події."""
    event = _get_accessible_event_or_404(pk, request.user)
    
    is_owner = event.user == request.user
    participant_record = EventParticipant.objects.filter(
        event=event, 
        participant=request.user
    ).first()
    is_participant = participant_record and participant_record.status == EventParticipant.Status.ACCEPTED
    
    scenario = event.scenario

    recommendations = build_recommendations_placeholder(
        user=request.user,
        scenario=scenario,
        drink=event.drink,
        dish=event.dish,
        people_count=event.people_count,
        duration_hours=event.duration_hours,
    )

    recovery_advice = build_recovery_advice(
        user=request.user,
        drink=event.drink,
        recommendations=recommendations,
    )
    
    # Отримуємо учасників
    participants = event.event_participants.select_related('participant__profile').all()
    accepted_participants = [p for p in participants if p.status == EventParticipant.Status.ACCEPTED]
    
    # Кількість повідомлень в обговоренні
    messages_count = EventMessage.objects.filter(event=event).count()

    return render(
        request,
        "events/event_detail.html",
        {
            "event": event,
            "scenario": scenario,
            "recommendations": recommendations,
            "recovery_advice": recovery_advice,
            "is_owner": is_owner,
            "is_participant": is_participant,
            "participants": participants,
            "accepted_participants": accepted_participants,
            "messages_count": messages_count,
        },
    )


@require_POST
@login_required
@adult_required
def event_recommendations_preview(request):
    """AJAX-ендпоінт для попереднього перегляду рекомендацій."""
    scenario_id = request.POST.get("scenario_id")
    drink_id = request.POST.get("drink_id")
    dish_id = request.POST.get("dish_id")

    people_count = request.POST.get("people_count")
    duration_hours = request.POST.get("duration_hours")

    scenario = get_object_or_404(Scenario, id=scenario_id)
    drink = get_object_or_404(Drink, id=drink_id) if drink_id else None
    dish = get_object_or_404(Dish, id=dish_id) if dish_id else None

    rec = build_recommendations_placeholder(
        request.user,
        scenario,
        drink,
        dish,
        people_count=people_count,
        duration_hours=duration_hours,
    )
    return JsonResponse(rec)


@login_required
@adult_required
def event_location(request, pk):
    """Сторінка з картою місця проведення події."""
    event = _get_accessible_event_or_404(pk, request.user)
    return render(request, "events/event_location.html", {"event": event})


@login_required
@adult_required
def event_feedback(request, pk):
    """Фідбек після події - оцінка та відгук."""
    event = _get_accessible_event_or_404(pk, request.user)
    
    if request.method == "POST":
        from django.utils import timezone
        
        rating = request.POST.get("rating")
        feedback_text = request.POST.get("feedback", "").strip()
        
        if rating:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    event.user_rating = rating
            except ValueError:
                pass
        
        event.feedback = feedback_text
        event.feedback_submitted_at = timezone.now()
        event.is_finished = True
        event.save()
        
        # Нараховуємо бали за завершення та оцінку події
        from gamification.services import award_points
        award_points(request.user, 'event_complete')
        if rating:
            award_points(request.user, 'event_rate')
        
        return redirect("events:event_detail", pk=event.pk)
    
    # Отримати відгуки учасників
    participants = event.event_participants.select_related('participant__profile').filter(
        feedback_submitted_at__isnull=False
    )
    
    return render(request, "events/event_feedback.html", {
        "event": event,
        "participants": participants,
        "average_rating": event.get_average_rating(),
    })


@login_required
@adult_required
def event_discussion(request, pk):
    """Обговорення події (чат учасників)."""
    event = _get_accessible_event_or_404(pk, request.user)
    
    is_owner = event.user == request.user
    
    # Отримуємо повідомлення
    event_messages = event.messages.select_related('user__profile').all()
    
    # Обробка нового повідомлення
    if request.method == "POST":
        text = request.POST.get("message", "").strip()
        if text:
            EventMessage.objects.create(
                event=event,
                user=request.user,
                text=text
            )
            return redirect("events:event_discussion", pk=pk)
    
    return render(request, "events/event_discussion.html", {
        "event": event,
        "messages_list": event_messages,
        "is_owner": is_owner,
    })


@login_required
@adult_required
def event_search_api(request):
    """AJAX API для пошуку подій по назві."""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'events': []})
    
    # Шукаємо події користувача (власні та де учасник)
    events = Event.objects.filter(
        Q(user=request.user) |
        Q(
            event_participants__participant=request.user,
            event_participants__status=EventParticipant.Status.ACCEPTED
        )
    ).filter(
        Q(title__icontains=query) |
        Q(scenario__name__icontains=query)
    ).select_related("scenario").distinct().order_by("-date")[:10]
    
    results = []
    for event in events:
        results.append({
            'id': event.pk,
            'title': event.title or event.scenario.name,
            'date': event.date.strftime('%d.%m.%Y') if event.date else '',
            'url': f'/events/events/{event.pk}/',
            'is_finished': event.is_finished,
        })
    
    return JsonResponse({'events': results})


@login_required
@adult_required
def event_deleted(request):
    """Сторінка підтвердження видалення події."""
    return render(request, "events/event_deleted.html")
