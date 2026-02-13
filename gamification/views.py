import json
import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import UserScore, Achievement, UserAchievement, Challenge, UserChallenge
from recipes.models import Cocktail


@login_required
def leaderboard(request):
    """Рейтинг користувачів з подіумом та таблицею лідерів."""
    period = request.GET.get('period', 'all')
    
    # Отримуємо всіх користувачів з балами
    scores = UserScore.objects.select_related("user", "user__profile").order_by("-points_total")
    
    # Загальна кількість користувачів з балами
    total_users = scores.count()
    
    # Топ-3 для подіуму
    top_3 = list(scores[:3])
    
    # Всі для таблиці (до 15 для 3 колонок)
    all_scores = list(scores[:15])
    
    # Позиція поточного користувача
    user_rank = None
    user_score = None
    percentile = None
    
    try:
        user_score = UserScore.objects.get(user=request.user)
        # Рахуємо скільки людей має більше балів
        higher_scores = UserScore.objects.filter(points_total__gt=user_score.points_total).count()
        user_rank = higher_scores + 1
        
        # Відсоток
        if total_users > 0:
            percentile = int((1 - (user_rank / total_users)) * 100)
    except UserScore.DoesNotExist:
        pass
    
    # Розбиваємо на 3 колонки по 5
    column_1 = all_scores[0:5]
    column_2 = all_scores[5:10]
    column_3 = all_scores[10:15]
    
    return render(request, "gamification/leaderboard.html", {
        "scores": scores,
        "top_3": top_3,
        "column_1": column_1,
        "column_2": column_2,
        "column_3": column_3,
        "user_rank": user_rank,
        "user_score": user_score,
        "percentile": percentile,
        "period": period,
        "total_users": total_users,
    })


@login_required
def my_achievements(request):
    achievements = UserAchievement.objects.filter(user=request.user).select_related("achievement")
    return render(request, "gamification/my_achievements.html", {"achievements": achievements})


@login_required
def challenges_list(request):
    """Список активних челенджів та прогрес користувача."""
    active_challenges = Challenge.objects.filter(is_active=True).order_by("-created_at")
    
    # Отримуємо або створюємо UserChallenge для кожного активного челенджу
    # та готуємо дані у форматі зручній для шаблону
    challenges_data = []
    for challenge in active_challenges:
        uc, created = UserChallenge.objects.get_or_create(
            user=request.user,
            challenge=challenge,
        )
        challenges_data.append({
            'challenge': challenge,
            'user_challenge': uc,
        })
    
    return render(request, "gamification/challenges.html", {
        "challenges_data": challenges_data,
    })


@login_required
def claim_challenge_reward(request, challenge_id):
    """Отримати нагороду за виконаний челендж."""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    user_challenge = get_object_or_404(UserChallenge, user=request.user, challenge=challenge)
    
    if user_challenge.status == UserChallenge.Status.CLAIMED:
        messages.warning(request, "Ви вже отримали нагороду за цей челендж.")
        return redirect("gamification:challenges")
    
    if not user_challenge.is_complete:
        messages.error(request, "Челендж ще не виконано.")
        return redirect("gamification:challenges")
    
    # Нараховуємо бали
    user_score, _ = UserScore.objects.get_or_create(user=request.user)
    user_score.points_total += challenge.points_reward
    user_score.save()
    
    # Оновлюємо статус
    user_challenge.status = UserChallenge.Status.CLAIMED
    user_challenge.completed_at = timezone.now()
    user_challenge.save()
    
    messages.success(request, f"Вітаємо! Ви отримали {challenge.points_reward} балів за «{challenge.title}»!")
    return redirect("gamification:challenges")


# ============ MINI-GAMES ============

@login_required
def cocktail_quiz(request):
    """Mini-game: Guess the cocktail by ingredients."""
    return render(request, "gamification/cocktail_quiz.html")


@login_required
def cocktail_quiz_question(request):
    """API: Get random cocktail question."""
    from django.db.models import Q
    
    # Get cocktails that are active AND have ingredients
    cocktails = list(
        Cocktail.objects.filter(
            is_active=True,
            ingredients__isnull=False
        )
        .prefetch_related('ingredients__ingredient')
        .distinct()
    )
    
    if len(cocktails) < 4:
        return JsonResponse({
            "error": f"Not enough cocktails in database (found {len(cocktails)}, need 4)"
        }, status=400)
    
    # Pick correct answer
    correct = random.choice(cocktails)
    
    # Get ingredients for the question
    ingredients = [
        ci.ingredient.name 
        for ci in correct.ingredients.all()[:5]
    ]
    
    # Pick 3 wrong answers
    wrong_cocktails = [c for c in cocktails if c.id != correct.id]
    wrong = random.sample(wrong_cocktails, min(3, len(wrong_cocktails)))
    
    # Create options
    options = [{"id": correct.id, "name": correct.name}]
    options.extend([{"id": c.id, "name": c.name} for c in wrong])
    random.shuffle(options)
    
    return JsonResponse({
        "question_type": "ingredients",
        "ingredients": ingredients,
        "description": correct.description[:100] if correct.description else None,
        "options": options,
        "correct_id": correct.id,
    })


@login_required
@require_POST
def cocktail_quiz_answer(request):
    """API: Check answer and award points."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    answer_id = data.get("answer_id")
    correct_id = data.get("correct_id")
    
    if not answer_id or not correct_id:
        return JsonResponse({"error": "Missing data"}, status=400)
    
    is_correct = int(answer_id) == int(correct_id)
    points_earned = 0
    
    if is_correct:
        # Award 5 points for correct answer
        points_earned = 5
        user_score, _ = UserScore.objects.get_or_create(user=request.user)
        user_score.points_total += points_earned
        user_score.save()
    
    # Get correct cocktail name
    try:
        correct_cocktail = Cocktail.objects.get(id=correct_id)
        correct_name = correct_cocktail.name
    except Cocktail.DoesNotExist:
        correct_name = "Unknown"
    
    return JsonResponse({
        "is_correct": is_correct,
        "correct_name": correct_name,
        "points_earned": points_earned,
    })
