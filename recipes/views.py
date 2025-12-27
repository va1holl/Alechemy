import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST

from accounts.decorators import premium_required
from .models import Cocktail, CocktailIngredient, CocktailReview, CocktailCategory, CocktailStrength
from events.models import Ingredient, Drink, Scenario, Event


# Список коктейлів, пошук за назвою

def cocktail_list(request):
    from django.db.models import Avg
    
    q = request.GET.get("q", "")
    alcohol = request.GET.get("alcohol", "")  # all, with, without
    min_rating = request.GET.get("rating", "")  # 1-5
    category = request.GET.get("category", "")  # shot, classic, tiki, etc.
    strength = request.GET.get("strength", "")  # light, medium, strong, very_strong
    
    cocktails = Cocktail.objects.filter(is_active=True).prefetch_related('ingredients__ingredient', 'reviews')
    
    if q:
        cocktails = cocktails.filter(name__icontains=q)
    
    # Фільтр по алкоголю (перевіряємо наявність алкогольних інгредієнтів)
    if alcohol == "with":
        cocktails = cocktails.filter(ingredients__ingredient__is_alcoholic=True).distinct()
    elif alcohol == "without":
        cocktails = cocktails.exclude(ingredients__ingredient__is_alcoholic=True)
    
    # Фільтр по категорії
    if category:
        cocktails = cocktails.filter(category=category)
    
    # Фільтр по міцності
    if strength:
        cocktails = cocktails.filter(strength=strength)
    
    # Фільтр по рейтингу
    if min_rating:
        try:
            min_r = int(min_rating)
            cocktails = cocktails.annotate(avg_r=Avg('reviews__rating')).filter(avg_r__gte=min_r)
        except ValueError:
            pass
    
    # Список категорій та міцностей для фільтрів
    categories = CocktailCategory.choices
    strengths = CocktailStrength.choices
    
    return render(request, "recipes/cocktail_list.html", {
        "cocktails": cocktails, 
        "q": q,
        "alcohol": alcohol,
        "min_rating": min_rating,
        "category": category,
        "strength": strength,
        "categories": categories,
        "strengths": strengths,
    })

# Деталі коктейлю

def cocktail_detail(request, slug):
    cocktail = get_object_or_404(
        Cocktail.objects.prefetch_related('ingredients__ingredient', 'reviews__user'),
        slug=slug, 
        is_active=True
    )
    
    # Отримуємо події користувача для можливості додавання коктейлю
    user_events = []
    user_review = None
    if request.user.is_authenticated:
        user_events = Event.objects.filter(user=request.user).select_related('scenario').order_by('-date')[:10]
        user_review = CocktailReview.objects.filter(cocktail=cocktail, user=request.user).first()
    
    return render(request, "recipes/cocktail_detail.html", {
        "cocktail": cocktail,
        "user_events": user_events,
        "user_review": user_review,
    })


@login_required
@require_POST
def add_cocktail_review(request, slug):
    """Додати або оновити відгук на коктейль."""
    cocktail = get_object_or_404(Cocktail, slug=slug, is_active=True)
    
    rating = request.POST.get("rating", "5")
    text = request.POST.get("text", "").strip()
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            rating = 5
    except (ValueError, TypeError):
        rating = 5
    
    review, created = CocktailReview.objects.update_or_create(
        cocktail=cocktail,
        user=request.user,
        defaults={
            "rating": rating,
            "text": text,
        }
    )
    
    if created:
        messages.success(request, "Дякуємо за відгук!")
    else:
        messages.success(request, "Відгук оновлено!")
    
    return redirect("recipes:cocktail_detail", slug=slug)

# Пошук за інгредієнтами

def cocktail_search_by_ingredients(request):
    # Тільки інгредієнти, які використовуються в коктейлях
    cocktail_ingredient_ids = CocktailIngredient.objects.values_list('ingredient_id', flat=True).distinct()
    ingredients = Ingredient.objects.filter(id__in=cocktail_ingredient_ids).order_by("name")
    
    selected = request.GET.getlist("ingredients")
    cocktails = Cocktail.objects.filter(is_active=True).prefetch_related('ingredients__ingredient')
    if selected:
        cocktails = cocktails.filter(ingredients__ingredient__in=selected).distinct()
    return render(request, "recipes/cocktail_search.html", {"ingredients": ingredients, "selected": selected, "cocktails": cocktails})


# ===============================
# AI-Сомельє (Premium Feature)
# ===============================
# Інтелектуальна система рекомендацій на основі:
# - Сценарію події
# - Смакових уподобань
# - Історії користувача
# - Сезонності та часу доби

def _get_user_preferences(user):
    """Аналізує історію користувача для персоналізації."""
    from collections import Counter
    from django.db.models import Count
    
    preferences = {
        "favorite_drinks": [],
        "favorite_cocktails": [],
        "preferred_strength": "regular",
        "avg_rating": 0,
    }
    
    # Аналіз подій користувача
    events = Event.objects.filter(user=user).select_related('drink').order_by('-date')[:20]
    drink_counter = Counter()
    for e in events:
        if e.drink:
            drink_counter[e.drink.id] += 1
    
    if drink_counter:
        preferences["favorite_drinks"] = [d[0] for d in drink_counter.most_common(3)]
    
    # Аналіз відгуків на коктейлі
    reviews = CocktailReview.objects.filter(user=user).select_related('cocktail')
    if reviews.exists():
        high_rated = reviews.filter(rating__gte=4).values_list('cocktail_id', flat=True)
        preferences["favorite_cocktails"] = list(high_rated)[:5]
        preferences["avg_rating"] = sum(r.rating for r in reviews) / reviews.count()
    
    return preferences


def _score_drink(drink, scenario, taste, strength, mood, preferences):
    """Розраховує score для напою на основі всіх факторів."""
    score = 0
    
    # Базовий score
    score += 10
    
    # Відповідність сценарію (+30)
    if scenario and scenario.drinks.filter(id=drink.id).exists():
        score += 30
    
    # Відповідність міцності (+20)
    if strength == "light" and drink.strength in ["regular", "non_alcoholic"]:
        score += 20
    elif strength == "strong" and drink.strength == "strong":
        score += 20
    elif strength == "regular" and drink.strength == "regular":
        score += 15
    
    # Улюблений напій користувача (+25)
    if drink.id in preferences.get("favorite_drinks", []):
        score += 25
    
    # Відповідність настрою
    mood_mapping = {
        "party": ["strong", "regular"],
        "relaxed": ["regular", "light"],
        "romantic": ["regular", "light"],
    }
    if drink.strength in mood_mapping.get(mood, []):
        score += 10
    
    # Бонус за опис (якість контенту)
    if drink.description and len(drink.description) > 50:
        score += 5
    
    return score


def _score_cocktail(cocktail, scenario, taste, strength, mood, preferences):
    """Розраховує score для коктейлю на основі всіх факторів."""
    score = 0
    
    # Базовий score
    score += 10
    
    # Улюблений коктейль користувача (+25)
    if cocktail.id in preferences.get("favorite_cocktails", []):
        score += 25
    
    # Рейтинг коктейлю
    reviews = cocktail.reviews.all()
    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()
        score += int(avg_rating * 5)  # До +25
    
    # Відповідність смаку
    taste_keywords = {
        "sweet": ["солодкий", "sweet", "цукор", "сироп", "лікер"],
        "dry": ["сухий", "dry", "гіркий", "bitter", "вермут"],
        "balanced": [],
    }
    desc_lower = (cocktail.description or "").lower()
    for keyword in taste_keywords.get(taste, []):
        if keyword in desc_lower:
            score += 15
            break
    
    # Складність приготування (для relaxed - простіші)
    ingredients_count = cocktail.ingredients.count()
    if mood == "relaxed" and ingredients_count <= 4:
        score += 10
    elif mood == "party" and ingredients_count <= 5:
        score += 5
    
    # Бонус за фото
    if hasattr(cocktail, 'image') and cocktail.image:
        score += 5
    
    return score


@login_required
@premium_required
def ai_sommelier(request):
    """
    AI-Сомельє: інтелектуальні рекомендації напоїв та коктейлів на основі:
    - Обраного сценарію
    - Смакових уподобань (сухе/солодке, міцне/легке)
    - Настрою
    - Історії користувача
    """
    scenarios = Scenario.objects.all().order_by("name")
    drinks = Drink.objects.all()
    cocktails = Cocktail.objects.filter(is_active=True).prefetch_related('ingredients', 'reviews')
    
    recommendation = None
    recommendation_type = None
    explanation = ""
    alternatives = []
    
    if request.method == "POST":
        scenario_id = request.POST.get("scenario")
        taste = request.POST.get("taste", "balanced")  # sweet, dry, balanced
        strength = request.POST.get("strength", "regular")  # light, regular, strong
        mood = request.POST.get("mood", "relaxed")  # party, relaxed, romantic
        prefer_type = request.POST.get("prefer_type", "any")  # drink, cocktail, any
        
        # Отримуємо уподобання користувача
        preferences = _get_user_preferences(request.user)
        
        # Отримуємо сценарій
        scenario = None
        if scenario_id:
            try:
                scenario = Scenario.objects.get(id=scenario_id)
            except Scenario.DoesNotExist:
                pass
        
        # Скоринг напоїв
        scored_drinks = []
        for drink in drinks:
            score = _score_drink(drink, scenario, taste, strength, mood, preferences)
            scored_drinks.append((drink, score, "drink"))
        
        # Скоринг коктейлів
        scored_cocktails = []
        for cocktail in cocktails:
            score = _score_cocktail(cocktail, scenario, taste, strength, mood, preferences)
            scored_cocktails.append((cocktail, score, "cocktail"))
        
        # Об'єднуємо та сортуємо
        all_recommendations = []
        if prefer_type in ["any", "drink"]:
            all_recommendations.extend(scored_drinks)
        if prefer_type in ["any", "cocktail"]:
            all_recommendations.extend(scored_cocktails)
        
        # Сортуємо за score (найвищий спочатку)
        all_recommendations.sort(key=lambda x: x[1], reverse=True)
        
        # Беремо топ рекомендацію
        if all_recommendations:
            recommendation, score, recommendation_type = all_recommendations[0]
            
            # Генеруємо пояснення на основі факторів
            if recommendation_type == "drink":
                explanation = _generate_smart_drink_explanation(recommendation, scenario, mood, taste, score)
            else:
                explanation = _generate_smart_cocktail_explanation(recommendation, mood, taste, score)
            
            # Альтернативи (наступні 3)
            alternatives = [(item, itype) for item, s, itype in all_recommendations[1:4]]
    
    return render(request, "recipes/ai_sommelier.html", {
        "scenarios": scenarios,
        "recommendation": recommendation,
        "recommendation_type": recommendation_type,
        "explanation": explanation,
        "alternatives": alternatives,
    })


@login_required
@premium_required
def ai_sommelier_api(request):
    """JSON API для AJAX запитів від AI-Сомельє."""
    scenario_id = request.GET.get("scenario")
    taste = request.GET.get("taste", "balanced")
    strength = request.GET.get("strength", "regular")
    mood = request.GET.get("mood", "relaxed")
    prefer_type = request.GET.get("prefer_type", "any")
    
    drinks = Drink.objects.all()
    cocktails = Cocktail.objects.filter(is_active=True).prefetch_related('ingredients', 'reviews')
    
    # Отримуємо уподобання користувача
    preferences = _get_user_preferences(request.user)
    
    # Отримуємо сценарій
    scenario = None
    if scenario_id:
        try:
            scenario = Scenario.objects.get(id=scenario_id)
        except Scenario.DoesNotExist:
            pass
    
    # Скоринг
    all_recommendations = []
    
    if prefer_type in ["any", "drink"]:
        for drink in drinks:
            score = _score_drink(drink, scenario, taste, strength, mood, preferences)
            all_recommendations.append((drink, score, "drink"))
    
    if prefer_type in ["any", "cocktail"]:
        for cocktail in cocktails:
            score = _score_cocktail(cocktail, scenario, taste, strength, mood, preferences)
            all_recommendations.append((cocktail, score, "cocktail"))
    
    # Сортуємо за score
    all_recommendations.sort(key=lambda x: x[1], reverse=True)
    
    if all_recommendations:
        item, score, item_type = all_recommendations[0]
        
        if item_type == "drink":
            return JsonResponse({
                "type": "drink",
                "name": item.name,
                "description": item.description or "",
                "abv": str(item.abv) if item.abv else None,
                "explanation": _generate_smart_drink_explanation(item, scenario, mood, taste, score),
                "score": score,
            })
        else:
            return JsonResponse({
                "type": "cocktail",
                "name": item.name,
                "slug": item.slug,
                "description": item.description or "",
                "explanation": _generate_smart_cocktail_explanation(item, mood, taste, score),
                "score": score,
            })
    
    return JsonResponse({"error": "Рекомендацій не знайдено"}, status=404)


def _generate_smart_drink_explanation(drink, scenario, mood, taste, score):
    """Генерує розумне пояснення для рекомендованого напою."""
    parts = []
    
    # Основна рекомендація
    if score >= 50:
        parts.append(f"🎯 **{drink.name}** — ідеальний вибір для вас!")
    elif score >= 30:
        parts.append(f"👍 **{drink.name}** — чудовий варіант.")
    else:
        parts.append(f"🍷 Спробуйте **{drink.name}**.")
    
    # Чому саме цей напій
    reasons = []
    
    if scenario and scenario.drinks.filter(id=drink.id).exists():
        reasons.append(f"відмінно підходить для сценарію «{scenario.name}»")
    
    mood_reasons = {
        "party": "підніме настрій на вечірці",
        "relaxed": "допоможе розслабитись",
        "romantic": "створить романтичну атмосферу",
    }
    if mood in mood_reasons:
        reasons.append(mood_reasons[mood])
    
    if drink.abv:
        if drink.abv < 15:
            reasons.append("легкий та освіжаючий")
        elif drink.abv > 35:
            reasons.append("для справжніх цінителів")
    
    if reasons:
        parts.append("Цей напій " + ", ".join(reasons) + ".")
    
    if drink.description:
        parts.append(f"\n\n_{drink.description[:150]}{'...' if len(drink.description) > 150 else ''}_")
    
    return " ".join(parts)


def _generate_smart_cocktail_explanation(cocktail, mood, taste, score):
    """Генерує розумне пояснення для рекомендованого коктейлю."""
    parts = []
    
    # Основна рекомендація
    if score >= 50:
        parts.append(f"🍹 **{cocktail.name}** — топ рекомендація для вас!")
    elif score >= 30:
        parts.append(f"🥂 **{cocktail.name}** — відмінний вибір.")
    else:
        parts.append(f"🍸 Рекомендуємо спробувати **{cocktail.name}**.")
    
    # Рейтинг
    reviews = cocktail.reviews.all()
    if reviews.exists():
        avg = sum(r.rating for r in reviews) / reviews.count()
        if avg >= 4.5:
            parts.append(f"⭐ Рейтинг {avg:.1f}/5 — улюбленець користувачів!")
        elif avg >= 4:
            parts.append(f"⭐ Високий рейтинг {avg:.1f}/5.")
    
    # Складність
    ing_count = cocktail.ingredients.count()
    if ing_count <= 3:
        parts.append("Простий у приготуванні.")
    elif ing_count >= 6:
        parts.append("Складний але вартий того.")
    
    # Настрій
    mood_phrases = {
        "party": "🎉 Ідеально для вечірки!",
        "relaxed": "🌙 Для спокійного вечора.",
        "romantic": "💕 Романтичний вибір.",
    }
    if mood in mood_phrases:
        parts.append(mood_phrases[mood])
    
    if cocktail.description:
        parts.append(f"\n\n_{cocktail.description[:150]}{'...' if len(cocktail.description) > 150 else ''}_")
    
    return " ".join(parts)
