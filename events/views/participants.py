"""
Participants views - invites, participants management, admin toggles.
"""
import logging

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from accounts.decorators import adult_required
from accounts.models import User, FriendRequest, Notification
from gamification.services import award_points
from ..models import Event, EventParticipant, EventMessage
from .utils import (
    _get_accessible_event_or_404,
    _get_admin_event_or_404,
    _get_owner_event_or_404,
)

logger = logging.getLogger(__name__)


@login_required
@adult_required
def event_participants(request, pk):
    """Список учасників події з функцією запрошення."""
    event = _get_accessible_event_or_404(pk, request.user)
    is_owner = event.user == request.user
    # Check if user has HEAD role (admin-like privileges)
    is_admin = EventParticipant.objects.filter(
        event=event, 
        participant=request.user, 
        role=EventParticipant.Role.HEAD
    ).exists() or is_owner
    
    participants = event.event_participants.select_related('participant__profile').all()
    
    # Пошук користувачів для запрошення (тільки для адмінів)
    search_query = request.GET.get('q', '').strip()
    search_results = []
    
    if is_admin and search_query:
        clean_query = search_query.lstrip('#@')
        users = User.objects.filter(
            Q(profile__unique_tag__icontains=clean_query) |
            Q(profile__display_name__icontains=clean_query) |
            Q(first_name__icontains=clean_query)
        ).exclude(
            pk=request.user.pk
        ).select_related('profile')[:15]
        
        for u in users:
            u.is_invited = EventParticipant.objects.filter(event=event, participant=u).exists()
            search_results.append(u)
    
    # Список друзів для швидкого запрошення (перші 6)
    friends_preview = []
    if is_admin:
        friendships = FriendRequest.objects.filter(
            Q(from_user=request.user, status=FriendRequest.Status.ACCEPTED) |
            Q(to_user=request.user, status=FriendRequest.Status.ACCEPTED)
        ).select_related('from_user__profile', 'to_user__profile')[:6]
        
        for f in friendships:
            friend = f.to_user if f.from_user == request.user else f.from_user
            friend.profile.is_invited = EventParticipant.objects.filter(event=event, participant=friend).exists()
            friends_preview.append(friend.profile)
    
    # Обробка POST запиту для запрошення
    if request.method == "POST" and is_admin:
        user_id = request.POST.get("user_id")
        if user_id:
            target_user = get_object_or_404(User, pk=user_id)
            
            if target_user == request.user:
                messages.error(request, _("Ви не можете запросити себе"))
            else:
                user_display = target_user.profile.get_display_name() if hasattr(target_user, 'profile') else target_user.first_name or "Користувач"
                
                participant, created = EventParticipant.objects.get_or_create(
                    event=event,
                    participant=target_user,
                    defaults={'status': EventParticipant.Status.PENDING}
                )
                if created:
                    messages.success(request, f"Запрошення надіслано {user_display}")
                    award_points(request.user, 'event_invite')
                    
                    Notification.objects.create(
                        user=target_user,
                        notification_type=Notification.NotificationType.EVENT_INVITE,
                        title="Запрошення на подію",
                        message=f"запросив вас на подію «{event.title or event.scenario.name}»",
                        action_required=True,
                        action_url=reverse("events:event_participants", kwargs={"pk": event.pk}),
                        related_user=request.user,
                        related_event=event
                    )
                else:
                    messages.info(request, f"{user_display} вже запрошений.")
            
            redirect_url = reverse("events:event_participants", kwargs={"pk": pk})
            if search_query:
                redirect_url += f"?q={search_query}"
            return redirect(redirect_url)
    
    return render(request, "events/event_participants.html", {
        "event": event,
        "participants": participants,
        "is_owner": is_owner,
        "is_admin": is_admin,
        "search_query": search_query,
        "search_results": search_results,
        "friends_preview": friends_preview,
    })


@login_required
@adult_required
def event_invite_friend(request, pk):
    """Редірект на сторінку учасників (функціонал перенесено туди)."""
    # Зберігаємо пошуковий запит при редіректі
    search_query = request.GET.get('q', '').strip()
    redirect_url = reverse("events:event_participants", kwargs={"pk": pk})
    if search_query:
        redirect_url += f"?q={search_query}"
    return redirect(redirect_url)


@require_POST
@login_required
@adult_required
def event_remove_participant(request, pk, participant_pk):
    """Видалити учасника з події (тільки для власника/адміна)."""
    event = _get_admin_event_or_404(pk, request.user)
    
    participant = get_object_or_404(EventParticipant, event=event, pk=participant_pk)
    
    # Не можна видалити власника
    if participant.participant == event.user:
        messages.error(request, "Не можна видалити власника події")
        return redirect("events:event_participants", pk=pk)
    
    participant.delete()
    messages.success(request, "Учасника видалено")
    
    return redirect("events:event_participants", pk=pk)


@login_required
@adult_required
def event_invitation_response(request, pk, action):
    """Прийняти або відхилити запрошення."""
    event = get_object_or_404(Event, pk=pk)
    
    participant = get_object_or_404(
        EventParticipant, 
        event=event, 
        participant=request.user
    )
    
    if action == "accept":
        participant.status = EventParticipant.Status.ACCEPTED
        participant.responded_at = timezone.now()
        participant.save()
        messages.success(request, "Ви приєдналися до події")
        
        # Нараховуємо бали за участь
        from gamification.services import award_points
        award_points(request.user, 'event_join')
        
    elif action == "decline":
        participant.status = EventParticipant.Status.DECLINED
        participant.responded_at = timezone.now()
        participant.save()
        messages.info(request, "Ви відхилили запрошення")
    
    return redirect("events:event_list")


@require_POST
@login_required
@adult_required
def event_toggle_admin(request, pk, participant_pk):
    """Переключити права адміна учасника (змінює роль HEAD/PARTICIPANT)."""
    event = _get_owner_event_or_404(pk, request.user)
    
    participant = get_object_or_404(EventParticipant, event=event, pk=participant_pk)
    
    # Не можна змінити права власника
    if participant.participant == event.user:
        messages.error(request, "Не можна змінити права власника")
        return redirect("events:event_participants", pk=pk)
    
    # Toggle between HEAD and PARTICIPANT role
    if participant.role == EventParticipant.Role.HEAD:
        participant.role = EventParticipant.Role.PARTICIPANT
        messages.info(request, f"{participant.participant.get_full_name() or participant.participant.email} більше не адміністратор")
    else:
        participant.role = EventParticipant.Role.HEAD
        messages.success(request, f"{participant.participant.get_full_name() or participant.participant.email} тепер адміністратор")
    participant.save()
    
    return redirect("events:event_participants", pk=pk)


@require_POST
@login_required
@adult_required
def event_finish(request, pk):
    """Завершити подію."""
    event = _get_owner_event_or_404(pk, request.user)
    
    event.is_finished = True
    event.save()
    
    # Нараховуємо бали за завершення
    from gamification.services import award_points
    award_points(request.user, 'event_complete')
    
    messages.success(request, "Подія завершена")
    
    return redirect("events:event_feedback", pk=pk)


@login_required
@adult_required
def my_invitations(request):
    """Список запрошень для поточного користувача."""
    invitations = EventParticipant.objects.filter(
        participant=request.user,
        status=EventParticipant.Status.PENDING
    ).select_related('event__scenario', 'event__user__profile')
    
    return render(request, "events/my_invitations.html", {
        "invitations": invitations,
    })


@login_required
@adult_required
def event_leave(request, pk):
    """Покинути подію (для учасників)."""
    event = get_object_or_404(Event, pk=pk)
    
    # Власник не може покинути свою подію
    if event.user == request.user:
        messages.error(request, "Ви не можете покинути власну подію")
        return redirect("events:event_detail", pk=pk)
    
    participant = EventParticipant.objects.filter(
        event=event,
        participant=request.user
    ).first()
    
    if participant:
        participant.delete()
        messages.info(request, "Ви покинули подію")
    
    return redirect("events:event_list")
