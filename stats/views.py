import io
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count, Avg, Max
from django.db.models.functions import TruncMonth
from django.utils import timezone

from events.models import Event, AlcoholLog, Scenario
from gamification.models import UserScore, UserAchievement, UserChallenge
from accounts.decorators import premium_required


@login_required
@premium_required
def export_pdf_report(request):
    """Generate PDF report with user statistics (Premium feature)."""
    import os
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Register DejaVu font for Cyrillic support
    font_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux/Docker
        '/usr/share/fonts/dejavu/DejaVuSans.ttf',  # Alt Linux
        'C:/Windows/Fonts/arial.ttf',  # Windows fallback
    ]
    font_registered = False
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
                font_registered = True
                break
            except:
                continue
    
    # Fallback: try to use bundled font from static
    if not font_registered:
        static_font = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'DejaVuSans.ttf')
        if os.path.exists(static_font):
            pdfmetrics.registerFont(TTFont('DejaVuSans', static_font))
            font_registered = True
    
    FONT_NAME = 'DejaVuSans' if font_registered else 'Helvetica'
    
    user = request.user
    profile = getattr(user, "profile", None)
    
    # Collect statistics
    now = timezone.now()
    month_ago = now - timedelta(days=30)
    
    events = Event.objects.filter(user=user)
    events_total = events.count()
    events_month = events.filter(date__gte=month_ago.date()).count()
    
    logs = AlcoholLog.objects.filter(user=user)
    logs_total = logs.count()
    logs_month = logs.filter(taken_at__gte=month_ago).count()
    
    bac_stats = logs.aggregate(
        avg_bac=Avg("bac_estimate"),
        max_bac=Max("bac_estimate"),
        total_volume=Sum("volume_ml")
    )
    
    user_score = UserScore.objects.filter(user=user).first()
    points = user_score.points_total if user_score else 0
    achievements = UserAchievement.objects.filter(user=user).count()
    challenges_done = UserChallenge.objects.filter(user=user, status__in=["completed", "claimed"]).count()
    
    favorite_scenario = (
        events.values("scenario__name")
        .annotate(cnt=Count("id"))
        .order_by("-cnt")
        .first()
    )
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=FONT_NAME,
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#34A853')
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=FONT_NAME,
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#34A853')
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=11,
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("Alechemy — Звіт користувача", title_style))
    elements.append(Paragraph(f"Користувач: {user.email}", normal_style))
    elements.append(Paragraph(f"Дата створення: {now.strftime('%d.%m.%Y %H:%M')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Events section
    elements.append(Paragraph("📅 Статистика подій", heading_style))
    events_data = [
        ["Показник", "Значення"],
        ["Всього подій", str(events_total)],
        ["Подій за місяць", str(events_month)],
        ["Улюблений сценарій", favorite_scenario["scenario__name"] if favorite_scenario else "—"],
    ]
    events_table = Table(events_data, colWidths=[120*mm, 50*mm])
    events_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34A853')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    elements.append(events_table)
    elements.append(Spacer(1, 15))
    
    # Diary section
    elements.append(Paragraph("📊 Алко-щоденник", heading_style))
    avg_bac = f"{float(bac_stats['avg_bac']):.2f}‰" if bac_stats['avg_bac'] else "—"
    max_bac = f"{float(bac_stats['max_bac']):.2f}‰" if bac_stats['max_bac'] else "—"
    total_vol = f"{bac_stats['total_volume']} мл" if bac_stats['total_volume'] else "—"
    
    diary_data = [
        ["Показник", "Значення"],
        ["Всього записів", str(logs_total)],
        ["Записів за місяць", str(logs_month)],
        ["Середній BAC", avg_bac],
        ["Максимальний BAC", max_bac],
        ["Загальний об'єм", total_vol],
    ]
    diary_table = Table(diary_data, colWidths=[120*mm, 50*mm])
    diary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34A853')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    elements.append(diary_table)
    elements.append(Spacer(1, 15))
    
    # Gamification section
    elements.append(Paragraph("🏆 Гейміфікація", heading_style))
    gam_data = [
        ["Показник", "Значення"],
        ["Бали", str(points)],
        ["Досягнення", str(achievements)],
        ["Виконані челенджі", str(challenges_done)],
    ]
    gam_table = Table(gam_data, colWidths=[120*mm, 50*mm])
    gam_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34A853')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    elements.append(gam_table)
    elements.append(Spacer(1, 30))
    
    # Footer
    elements.append(Paragraph(
        "Цей звіт згенеровано автоматично системою Alechemy. "
        "Дані BAC є приблизними і не можуть використовуватися для медичних або юридичних цілей.",
        ParagraphStyle('Footer', parent=normal_style, fontName=FONT_NAME, fontSize=9, textColor=colors.grey)
    ))
    
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="alechemy_report_{now.strftime("%Y%m%d")}.pdf"'
    return response


@login_required
def dashboard(request):
    user = request.user
    profile = getattr(user, "profile", None)
    
    # Основна статистика
    events_count = Event.objects.filter(user=user).count()
    diary_entries = AlcoholLog.objects.filter(user=user).count()
    
    # Улюблений сценарій
    favorite_scenario = (
        Event.objects.filter(user=user)
        .values("scenario__name")
        .annotate(count=Count("id"))
        .order_by("-count")
        .first()
    )
    
    # Статистика по місяцях для графіка
    monthly_events = (
        Event.objects.filter(user=user)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )[:6]
    
    # BAC статистика
    bac_stats = AlcoholLog.objects.filter(user=user).aggregate(
        avg_bac=Avg("bac_estimate"),
        max_bac=Max("bac_estimate"),
        total_drinks=Count("id"),
    )
    
    # Гейміфікація
    user_score = UserScore.objects.filter(user=user).first()
    achievements_count = UserAchievement.objects.filter(user=user).count()
    challenges_in_progress = UserChallenge.objects.filter(
        user=user, status="in_progress"
    ).count()
    challenges_completed = UserChallenge.objects.filter(
        user=user, status__in=["completed", "claimed"]
    ).count()
    
    # Прогрес до наступного рівня (умовний)
    points = user_score.points_total if user_score else 0
    level = points // 100 + 1
    progress_to_next = points % 100
    
    # Середній BAC за останні записи - with select_related for drink
    recent_logs = (
        AlcoholLog.objects.filter(user=user)
        .select_related('drink')
        .order_by("-taken_at")[:10]
    )
    
    context = {
        "events_count": events_count,
        "diary_entries": diary_entries,
        "favorite_scenario": favorite_scenario,
        "monthly_events": list(monthly_events),
        "bac_stats": bac_stats,
        "user_score": user_score,
        "points": points,
        "level": level,
        "progress_to_next": progress_to_next,
        "achievements_count": achievements_count,
        "challenges_in_progress": challenges_in_progress,
        "challenges_completed": challenges_completed,
        "recent_logs": recent_logs,
    }
    
    return render(request, "stats/dashboard.html", context)
