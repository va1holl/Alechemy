"""
Participants views - invites, participants management, admin toggles.
"""
import logging

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages

from accounts.decorators import adult_required
from accounts.models import User, FriendRequest
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
    """Список учасників події."""
    event = _get_accessible_event_or_404(pk, request.user)
    is_owner = event.user == request.user
    # Check if user has HEAD role (admin-like privileges)
    is_admin = EventParticipant.objects.filter(
        event=event, 
        participant=request.user, 
        role=EventParticipant.Role.HEAD
    ).exists() or is_owner
    
    participants = event.event_participants.select_related('participant__profile').all()
    
    # Розділяємо на категорії
    accepted = [p for p in participants if p.status == EventParticipant.Status.ACCEPTED]
    pending = [p for p in participants if p.status == EventParticipant.Status.PENDING]
    declined = [p for p in participants if p.status == EventParticipant.Status.DECLINED]
    
    return render(request, "events/event_participants.html", {
        "event": event,
        "participants": participants,
        "accepted": accepted,
        "pending": pending,
        "declined": declined,
        "is_owner": is_owner,
        "is_admin": is_admin,
    })


@login_required
@adult_required
def event_invite_friend(request, pk):
    """Запросити друга на подію."""
    event = _get_admin_event_or_404(pk, request.user)
    
    # Отримуємо список друзів
    friendships = FriendRequest.objects.filter(
        Q(from_user=request.user, status=FriendRequest.Status.ACCEPTED) |
        Q(to_user=request.user, status=FriendRequest.Status.ACCEPTED)
    ).select_related('from_user__profile', 'to_user__profile')
    
    friends = []
    for f in friendships:
        friend = f.to_user if f.from_user == request.user else f.from_user
        # Перевіряємо чи вже запрошений
        is_invited = EventParticipant.objects.filter(
            event=event, 
            participant=friend
        ).exists()
        friends.append({
            'user': friend,
            'is_invited': is_invited,
        })
    
    if request.method == "POST":
        friend_id = request.POST.get("friend_id")
        if friend_id:
            friend = get_object_or_404(User, pk=friend_id)
            
            # Перевіряємо що це справді друг
            is_friend = FriendRequest.objects.filter(
                Q(from_user=request.user, to_user=friend, status=FriendRequest.Status.ACCEPTED) |
                Q(from_user=friend, to_user=request.user, status=FriendRequest.Status.ACCEPTED)
            ).exists()
            
            if is_friend:
                EventParticipant.objects.get_or_create(
                    event=event,
                    participant=friend,
                    defaults={
                        'status': EventParticipant.Status.PENDING,
                    }
                )
                messages.success(request, f"Запрошення надіслано {friend.get_full_name() or friend.email}")
            else:
                messages.error(request, "Ви можете запрошувати тільки друзів")
        
        return redirect("events:event_invite_friend", pk=pk)
    
    return render(request, "events/event_invite_friend.html", {
        "event": event,
        "friends": friends,
    })


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
