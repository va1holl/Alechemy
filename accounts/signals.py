from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """Створює профіль тільки для нового користувача."""
    if created:
        Profile.objects.get_or_create(user=instance)

# Прибрано save_profile_for_user - він створював зайві UPDATE при кожному User.save()
# Профіль зберігається окремо через profile.save() де потрібно
