"""
Email notification service for Alechemy.
Sends branded HTML emails for key user events.
Respects user's email_notifications preference.
"""
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger('accounts')


def _should_send(user):
    """Check if user has email notifications enabled."""
    profile = getattr(user, 'profile', None)
    if profile and not profile.email_notifications:
        return False
    return bool(user.email)


def _send(subject, template, context, recipient_email):
    """Send a branded HTML email."""
    domain = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')
    context.setdefault("domain", domain)
    context.setdefault("protocol", "https" if not settings.DEBUG else "http")

    html = render_to_string(template, context)
    plain = strip_tags(html)
    try:
        send_mail(
            subject=subject,
            message=plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html,
            fail_silently=True,
        )
    except Exception:
        logger.exception("Failed to send email to %s", recipient_email)


def send_welcome_email(user):
    """Send welcome email after successful registration."""
    if not _should_send(user):
        return
    _send(
        subject="Ласкаво просимо до Alechemy! 🍻",
        template="emails/welcome.html",
        context={"user": user},
        recipient_email=user.email,
    )


def send_event_invitation_email(invited_user, inviter, event):
    """Send email when user is invited to an event."""
    if not _should_send(invited_user):
        return
    inviter_name = _get_display_name(inviter)
    event_name = event.title or (event.scenario.name if event.scenario else "Подія")
    _send(
        subject=f"Вас запросили на подію «{event_name}»",
        template="emails/event_invitation.html",
        context={
            "user": invited_user,
            "inviter_name": inviter_name,
            "event": event,
            "event_name": event_name,
        },
        recipient_email=invited_user.email,
    )


def send_invitation_response_email(event_owner, responder, event, accepted):
    """Send email to event owner when someone accepts/declines invitation."""
    if not _should_send(event_owner):
        return
    responder_name = _get_display_name(responder)
    event_name = event.title or (event.scenario.name if event.scenario else "Подія")
    action = "прийняв(ла)" if accepted else "відхилив(ла)"
    _send(
        subject=f"{responder_name} {action} запрошення на «{event_name}»",
        template="emails/invitation_response.html",
        context={
            "user": event_owner,
            "responder_name": responder_name,
            "event": event,
            "event_name": event_name,
            "accepted": accepted,
        },
        recipient_email=event_owner.email,
    )


def _get_display_name(user):
    """Get user's display name for emails."""
    profile = getattr(user, 'profile', None)
    if profile and profile.display_name:
        return profile.display_name
    return user.first_name or user.email.split('@')[0]
