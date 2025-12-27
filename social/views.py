from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _

from accounts.models import FriendRequest, Profile


User = get_user_model()


@login_required
def friends_list(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    friends = profile.get_friends()
    incoming = request.user.received_friend_requests.filter(status=FriendRequest.Status.PENDING)
    outgoing = request.user.sent_friend_requests.filter(status=FriendRequest.Status.PENDING)

    return render(
        request,
        "social/friends_list.html",
        {
            "friends": friends,
            "incoming": incoming,
            "outgoing": outgoing,
            "search_results": None,
        },
    )


@login_required
@require_POST
def search_users(request):
    """Пошук користувачів за тегом або email."""
    query = request.POST.get("query", "").strip()
    profile, _ = Profile.objects.get_or_create(user=request.user)
    friends = profile.get_friends()
    incoming = request.user.received_friend_requests.filter(status=FriendRequest.Status.PENDING)
    outgoing = request.user.sent_friend_requests.filter(status=FriendRequest.Status.PENDING)
    
    search_results = []
    
    if query:
        # Видаляємо @ якщо є
        clean_query = query.lstrip("@").lower()
        
        # Отримуємо ID існуючих друзів і себе
        friends_ids = set(friends.values_list('id', flat=True))
        friends_ids.add(request.user.id)
        
        # Отримуємо ID користувачів з вхідними/вихідними запитами
        pending_ids = set(incoming.values_list('from_user_id', flat=True))
        pending_ids.update(outgoing.values_list('to_user_id', flat=True))
        
        # Виключаємо всіх
        exclude_ids = friends_ids | pending_ids
        
        # Шукаємо за тегом або email
        search_results = User.objects.filter(
            Q(profile__unique_tag__icontains=clean_query) |
            Q(email__icontains=clean_query)
        ).exclude(
            id__in=exclude_ids
        ).select_related('profile')[:10]
    
    return render(
        request,
        "social/friends_list.html",
        {
            "friends": friends,
            "incoming": incoming,
            "outgoing": outgoing,
            "search_results": search_results,
            "search_query": query,
        },
    )


@login_required
@require_POST
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, pk=user_id)
    if to_user == request.user:
        messages.error(request, _("Не можна додати себе в друзі."))
        return redirect("social:friends_list")

    friend_req, created = FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    if not created and friend_req.status == FriendRequest.Status.REJECTED:
        friend_req.status = FriendRequest.Status.PENDING
        friend_req.save()
        created = True  # Treat as new for notification
    
    # Створюємо сповіщення для отримувача
    if created:
        from accounts.models import Notification
        
        sender_name = request.user.profile.get_display_name() if hasattr(request.user, 'profile') else request.user.email
        
        Notification.objects.create(
            user=to_user,
            notification_type=Notification.NotificationType.FRIEND_REQUEST,
            title=_("Новий запит у друзі"),
            message=_("%(name)s хоче додати тебе в друзі") % {"name": sender_name},
            related_user=request.user,
            action_url=f"/social/friends/",
        )
        
        # Нараховуємо бали за відправку запиту в друзі
        from gamification.services import award_points
        award_points(request.user, 'friend_add')
        
        messages.success(request, _("Запит у друзі надіслано!"))
    else:
        messages.info(request, _("Запит вже надіслано раніше"))

    return redirect("social:friends_list")


@login_required
@require_POST
def accept_friend_request(request, req_id):
    req = get_object_or_404(FriendRequest, pk=req_id, to_user=request.user)
    req.accept()
    
    # Сповіщення відправнику про прийняття
    from accounts.models import Notification
    
    accepter_name = request.user.profile.get_display_name() if hasattr(request.user, 'profile') else request.user.email
    
    Notification.objects.create(
        user=req.from_user,
        notification_type=Notification.NotificationType.FRIEND_REQUEST,
        title=_("Запит прийнято!"),
        message=_("%(name)s прийняв твій запит у друзі") % {"name": accepter_name},
        related_user=request.user,
        response_action=Notification.ResponseAction.ACCEPTED,
    )
    
    # Нараховуємо бали обом користувачам за дружбу
    from gamification.services import award_points
    award_points(request.user, 'friend_accept')
    award_points(req.from_user, 'friend_accept')
    
    messages.success(request, _("Тепер ви друзі!"))
    
    return redirect("social:friends_list")


@login_required
@require_POST
def reject_friend_request(request, req_id):
    req = get_object_or_404(FriendRequest, pk=req_id, to_user=request.user)
    req.reject()
    return redirect("social:friends_list")


@login_required
def friends_leaderboard(request):
    """Рейтинг серед друзів за очками гейміфікації."""
    from gamification.models import UserScore
    from gamification.services import get_user_rank, get_leaderboard
    from django.db.models import F
    
    profile, _ = Profile.objects.get_or_create(user=request.user)
    friends = profile.get_friends()
    
    # Отримуємо ID друзів + свій (friends - це User objects, у них .id а не .user_id)
    friend_user_ids = [f.id for f in friends]
    friend_user_ids.append(request.user.id)
    
    # Рейтинг серед друзів
    leaderboard = (
        UserScore.objects
        .filter(user_id__in=friend_user_ids)
        .select_related('user__profile')
        .order_by('-points_total')
    )
    
    # Додаємо ранги до кожного запису
    leaderboard_with_ranks = []
    for idx, score in enumerate(leaderboard, 1):
        rank_info = get_user_rank(score.user)
        leaderboard_with_ranks.append({
            'position': idx,
            'score': score,
            'rank_info': rank_info,
        })
    
    # Знаходимо позицію поточного користувача
    user_rank = None
    user_rank_info = get_user_rank(request.user)
    for item in leaderboard_with_ranks:
        if item['score'].user_id == request.user.id:
            user_rank = item['position']
            break
    
    # Період фільтр (тиждень, місяць, весь час)
    period = request.GET.get('period', 'all')
    
    return render(request, "social/leaderboard.html", {
        "leaderboard": leaderboard_with_ranks,
        "user_rank": user_rank,
        "user_rank_info": user_rank_info,
        "period": period,
        "friends_count": len(friends),
    })


@login_required
def user_profile_by_tag(request, tag):
    """Перегляд профілю користувача за унікальним тегом."""
    # Нормалізуємо тег: видаляємо @ на початку, але залишаємо #
    tag = tag.lstrip("@")
    # Якщо тег без #, додаємо його для пошуку
    if not tag.startswith("#"):
        tag = "#" + tag
    
    target_profile = get_object_or_404(Profile.objects.select_related('user'), unique_tag__iexact=tag)
    
    # Перевірка чи це друг (get_friends повертає User objects)
    my_profile, _ = Profile.objects.get_or_create(user=request.user)
    my_friends = my_profile.get_friends()
    is_friend = target_profile.user in my_friends
    
    # Статистика
    from gamification.models import UserScore, UserAchievement
    from gamification.services import get_user_rank
    from events.models import Event
    
    user_score = UserScore.objects.filter(user=target_profile.user).first()
    rank_info = get_user_rank(target_profile.user)
    achievements_count = UserAchievement.objects.filter(user=target_profile.user).count()
    events_count = Event.objects.filter(user=target_profile.user).count()
    
    # Чи вже надіслано запит
    pending_request = None
    if not is_friend:
        pending_request = FriendRequest.objects.filter(
            from_user=request.user,
            to_user=target_profile.user,
            status=FriendRequest.Status.PENDING
        ).exists()
    
    return render(request, "social/user_profile.html", {
        "target_profile": target_profile,
        "is_friend": is_friend,
        "pending_request": pending_request,
        "user_score": user_score,
        "rank_info": rank_info,
        "achievements_count": achievements_count,
        "events_count": events_count,
    })
