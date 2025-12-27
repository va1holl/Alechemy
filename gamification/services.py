# gamification/services.py
"""
Сервіс для нарахування балів за різні активності.
"""
from django.db import transaction
from django.utils import timezone

# Конфігурація балів за активності
POINTS_CONFIG = {
    # Події
    'event_create': 10,           # Створення події
    'event_complete': 20,         # Завершення події (організатор)
    'event_rate': 5,              # Оцінка своєї події
    'event_invite': 3,            # Запрошення друга на подію
    'event_accept_invite': 5,     # Прийняття запрошення на подію
    'event_join': 5,              # Приєднання до події (alias для accept_invite)
    'event_participate': 10,      # Участь у завершеній події (учасник)
    'event_admin_complete': 15,   # Завершення події як адмін (не організатор)
    
    # Соціальні дії
    'friend_add': 5,              # Додавання друга
    'friend_accept': 5,           # Прийняття заявки в друзі
    'profile_complete': 15,       # Заповнення профілю (всі поля)
    
    # Алко-щоденник
    'diary_entry': 3,             # Запис у щоденнику
    
    # Контент
    'cocktail_view': 1,           # Перегляд рецепту коктейлю
    'place_visit': 2,             # Перегляд закладу на карті
    
    # Щоденні бонуси
    'daily_login': 2,             # Щоденний вхід
    'streak_7_days': 20,          # 7 днів підряд
    'streak_30_days': 100,        # 30 днів підряд
    
    # Ігри
    'quiz_correct': 5,            # Правильна відповідь у вікторині
    'quiz_complete': 10,          # Завершення вікторини
    
    # Покупки
    'shopping_list_create': 5,    # Створення списку покупок
    
    # Преміум
    'premium_subscribe': 50,      # Підписка на Premium
}


def award_points(user, action, multiplier=1):
    """
    Нараховує бали користувачу за певну дію.
    
    Args:
        user: Користувач Django
        action: Ключ дії з POINTS_CONFIG
        multiplier: Множник (наприклад, для подвійних балів)
    
    Returns:
        int: Кількість нарахованих балів, або 0 якщо дія не знайдена
    """
    from gamification.models import UserScore
    
    if action not in POINTS_CONFIG:
        return 0
    
    points = POINTS_CONFIG[action] * multiplier
    
    with transaction.atomic():
        user_score, created = UserScore.objects.get_or_create(user=user)
        user_score.points_total += points
        user_score.save()
    
    # Перевіряємо досягнення після нарахування балів
    check_achievements(user, action)
    
    return points


def check_achievements(user, action=None):
    """
    Перевіряє та нараховує досягнення користувачу.
    """
    from gamification.models import Achievement, UserAchievement, UserScore
    from events.models import Event
    
    achievements_earned = []
    
    # Отримуємо поточний рахунок
    user_score = UserScore.objects.filter(user=user).first()
    total_points = user_score.points_total if user_score else 0
    
    # Кількість подій
    events_count = Event.objects.filter(user=user).count()
    
    # Досягнення на основі балів
    point_milestones = [
        ('points_100', 100, 'Початківець', '🌱 Набрано 100 балів'),
        ('points_500', 500, 'Активіст', '⭐ Набрано 500 балів'),
        ('points_1000', 1000, 'Ентузіаст', '🏆 Набрано 1000 балів'),
        ('points_5000', 5000, 'Легенда', '👑 Набрано 5000 балів'),
    ]
    
    for code, required_points, title, desc in point_milestones:
        if total_points >= required_points:
            achievement, _ = Achievement.objects.get_or_create(
                code=code,
                defaults={'title': title, 'description': desc, 'points_reward': 10}
            )
            user_achievement, created = UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement
            )
            if created:
                achievements_earned.append(achievement)
                # Нараховуємо бонусні бали за досягнення
                if user_score:
                    user_score.points_total += achievement.points_reward
                    user_score.save()
    
    # Досягнення на основі подій
    event_milestones = [
        ('events_1', 1, 'Перша подія', '🎉 Створено першу подію'),
        ('events_5', 5, 'Організатор', '📅 Створено 5 подій'),
        ('events_10', 10, 'Досвідчений', '🎭 Створено 10 подій'),
        ('events_50', 50, 'Майстер подій', '🏅 Створено 50 подій'),
    ]
    
    for code, required_events, title, desc in event_milestones:
        if events_count >= required_events:
            achievement, _ = Achievement.objects.get_or_create(
                code=code,
                defaults={'title': title, 'description': desc, 'points_reward': 15}
            )
            user_achievement, created = UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement
            )
            if created:
                achievements_earned.append(achievement)
                if user_score:
                    user_score.points_total += achievement.points_reward
                    user_score.save()
    
    return achievements_earned


def get_user_rank(user):
    """
    Повертає ранг користувача на основі балів.
    Прикольні алкогольні назви рівнів!
    """
    from gamification.models import UserScore
    
    user_score = UserScore.objects.filter(user=user).first()
    points = user_score.points_total if user_score else 0
    
    ranks = [
        (0, 'Тверезий Новачок', '🥛'),
        (100, 'Перший Келих', '🍷'),
        (300, 'Весела Чарка', '🥃'),
        (500, 'Барний Філософ', '🍺'),
        (1000, 'Душа Компанії', '🎉'),
        (2000, 'Похмільний Воїн', '🤕'),
        (5000, 'Майстер Тостів', '🏆'),
        (10000, 'Легенда Застілля', '👑'),
    ]
    
    current_rank = ranks[0]
    next_rank = ranks[1] if len(ranks) > 1 else None
    
    for i, (threshold, name, icon) in enumerate(ranks):
        if points >= threshold:
            current_rank = (threshold, name, icon)
            if i + 1 < len(ranks):
                next_rank = ranks[i + 1]
            else:
                next_rank = None
    
    progress_to_next = 0
    if next_rank:
        points_in_rank = points - current_rank[0]
        points_needed = next_rank[0] - current_rank[0]
        progress_to_next = min(100, int(points_in_rank / points_needed * 100))
    
    return {
        'rank_name': current_rank[1],
        'rank_icon': current_rank[2],
        'points': points,
        'next_rank': next_rank[1] if next_rank else None,
        'next_rank_points': next_rank[0] if next_rank else None,
        'progress_to_next': progress_to_next,
    }


def get_leaderboard(limit=10):
    """
    Повертає таблицю лідерів.
    """
    from gamification.models import UserScore
    from accounts.models import Profile
    
    scores = UserScore.objects.select_related('user', 'user__profile').order_by('-points_total')[:limit]
    
    leaderboard = []
    for i, score in enumerate(scores, 1):
        profile = getattr(score.user, 'profile', None)
        rank_info = get_user_rank(score.user)
        
        leaderboard.append({
            'position': i,
            'user': score.user,
            'profile': profile,
            'points': score.points_total,
            'rank_name': rank_info['rank_name'],
            'rank_icon': rank_info['rank_icon'],
        })
    
    return leaderboard
