"""
Diary views - alcohol consumption tracking using AlcoholLog model.
"""
import json
import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Max, Sum
from django.db.models.functions import ExtractHour, ExtractWeekDay, TruncDate
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from accounts.decorators import adult_required
from ..models import AlcoholLog, Event
from ..forms import AlcoholLogForm
from .utils import _can_access_event

logger = logging.getLogger(__name__)


def get_diary_stats_for_user(user):
    """
    Отримати статистику щоденника для користувача.
    Повертає None якщо немає записів.
    """
    qs = AlcoholLog.objects.filter(user=user)

    if not qs.exists():
        return None

    last_log = qs.order_by("-taken_at").first()
    max_bac = qs.aggregate(Max("bac_estimate"))["bac_estimate__max"]

    return {
        "count": qs.count(),
        "max_bac": max_bac,
        "last_log": last_log,
    }


@login_required
@adult_required
def diary_list(request):
    """
    Список записей алко-дневника текущего пользователя з повною статистикою та графіками.
    """
    logs = (
        AlcoholLog.objects
        .filter(user=request.user)
        .select_related("event", "drink", "event__scenario")
        .order_by("-taken_at", "-created_at")
    )
    
    # === СТАТИСТИКА ===
    stats = {}
    
    if logs.exists():
        now = timezone.now()
        
        # Загальна статистика
        stats['total_logs'] = logs.count()
        stats['total_volume_ml'] = logs.aggregate(total=Sum('volume_ml'))['total'] or 0
        stats['avg_bac'] = logs.filter(bac_estimate__isnull=False).aggregate(avg=Avg('bac_estimate'))['avg']
        stats['max_bac'] = logs.filter(bac_estimate__isnull=False).aggregate(max=Max('bac_estimate'))['max']
        
        # Останній запис
        stats['last_log'] = logs.first()
        
        # Статистика за останній тиждень
        week_ago = now - timedelta(days=7)
        week_logs = logs.filter(taken_at__gte=week_ago)
        stats['week_logs'] = week_logs.count()
        stats['week_volume'] = week_logs.aggregate(total=Sum('volume_ml'))['total'] or 0
        
        # Статистика за останній місяць
        month_ago = now - timedelta(days=30)
        month_logs = logs.filter(taken_at__gte=month_ago)
        stats['month_logs'] = month_logs.count()
        stats['month_volume'] = month_logs.aggregate(total=Sum('volume_ml'))['total'] or 0
        
        # === ДАНІ ДЛЯ ГРАФІКІВ ===
        
        # 1. BAC по днях (останні 14 днів)
        two_weeks_ago = now - timedelta(days=14)
        bac_by_day = (
            logs.filter(taken_at__gte=two_weeks_ago, bac_estimate__isnull=False)
            .annotate(day=TruncDate('taken_at'))
            .values('day')
            .annotate(avg_bac=Avg('bac_estimate'), max_bac=Max('bac_estimate'))
            .order_by('day')
        )
        stats['bac_chart_labels'] = json.dumps([d['day'].strftime('%d.%m') for d in bac_by_day])
        stats['bac_chart_avg'] = json.dumps([float(d['avg_bac']) if d['avg_bac'] else 0 for d in bac_by_day])
        stats['bac_chart_max'] = json.dumps([float(d['max_bac']) if d['max_bac'] else 0 for d in bac_by_day])
        
        # 2. Об'єм споживання по днях (останні 14 днів)
        volume_by_day = (
            logs.filter(taken_at__gte=two_weeks_ago)
            .annotate(day=TruncDate('taken_at'))
            .values('day')
            .annotate(total_volume=Sum('volume_ml'))
            .order_by('day')
        )
        stats['volume_chart_labels'] = json.dumps([d['day'].strftime('%d.%m') for d in volume_by_day])
        stats['volume_chart_data'] = json.dumps([d['total_volume'] for d in volume_by_day])
        
        # 3. Розподіл за годинами (коли п'ють найчастіше)
        hourly_distribution = (
            logs
            .annotate(hour=ExtractHour('taken_at'))
            .values('hour')
            .annotate(count=Count('id'))
            .order_by('hour')
        )
        hours_data = {h['hour']: h['count'] for h in hourly_distribution}
        stats['hourly_labels'] = json.dumps([f"{h:02d}:00" for h in range(24)])
        stats['hourly_data'] = json.dumps([hours_data.get(h, 0) for h in range(24)])
        
        # 4. Розподіл за днями тижня
        weekday_distribution = (
            logs
            .annotate(weekday=ExtractWeekDay('taken_at'))
            .values('weekday')
            .annotate(count=Count('id'), total_volume=Sum('volume_ml'))
            .order_by('weekday')
        )
        weekday_names = ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
        weekday_data = {w['weekday']: w for w in weekday_distribution}
        stats['weekday_labels'] = json.dumps(weekday_names)
        stats['weekday_count'] = json.dumps([weekday_data.get(i, {}).get('count', 0) for i in range(1, 8)])
        stats['weekday_volume'] = json.dumps([weekday_data.get(i, {}).get('total_volume', 0) or 0 for i in range(1, 8)])
        
        # 5. Топ напоїв
        top_drinks = (
            logs.filter(drink__isnull=False)
            .values('drink__name')
            .annotate(count=Count('id'), total_volume=Sum('volume_ml'))
            .order_by('-count')[:5]
        )
        stats['top_drinks'] = list(top_drinks)
        stats['top_drinks_labels'] = json.dumps([d['drink__name'] for d in top_drinks])
        stats['top_drinks_data'] = json.dumps([d['count'] for d in top_drinks])
        
        # 6. Тренд BAC за місяць (тижневі середні)
        bac_trend = (
            logs.filter(taken_at__gte=month_ago, bac_estimate__isnull=False)
            .annotate(day=TruncDate('taken_at'))
            .values('day')
            .annotate(avg_bac=Avg('bac_estimate'))
            .order_by('day')
        )
        stats['bac_trend_labels'] = json.dumps([d['day'].strftime('%d.%m') for d in bac_trend])
        stats['bac_trend_data'] = json.dumps([float(d['avg_bac']) if d['avg_bac'] else 0 for d in bac_trend])
    
    return render(
        request,
        "events/diary_list.html",
        {"logs": logs, "stats": stats},
    )


@login_required
@adult_required
def diary_detail(request, pk):
    """Деталі запису щоденника."""
    log = get_object_or_404(AlcoholLog, pk=pk, user=request.user)
    return render(
        request,
        "events/diary_detail.html",
        {"log": log},
    )


@login_required
@adult_required
def diary_add(request, event_pk=None):
    """
    Додавання запису в щоденник.
    Якщо передано event_pk — прив'язуємо запис до цієї події (якщо є доступ).
    """
    event = None
    if event_pk is not None:
        event = get_object_or_404(Event, pk=event_pk)
        if not _can_access_event(event, request.user):
            messages.error(request, "У вас немає доступу до цієї події.")
            return redirect("events:event_list")

    if request.method == "POST":
        form = AlcoholLogForm(request.POST, user=request.user)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user

            if event is not None:
                log.event = event
            else:
                if log.event is not None and log.event.user_id != request.user.id:
                    form.add_error("event", "Не можна обрати чужу подію.")
                    return render(
                        request,
                        "events/diary_add.html",
                        {"form": form, "event": event},
                    )

            log.save()
            
            # Нараховуємо бали за ведення щоденника
            from gamification.services import award_points
            award_points(request.user, 'diary_entry')
            
            return redirect("events:diary_list")
    else:
        initial = {}
        if event is not None:
            initial["event"] = event
        form = AlcoholLogForm(initial=initial, user=request.user)

    return render(
        request,
        "events/diary_add.html",
        {"form": form, "event": event},
    )
