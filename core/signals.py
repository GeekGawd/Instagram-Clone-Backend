from urllib import request
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from rest_framework.response import Response

from core.models import Notification, User
from socialuser.models import Profile


@receiver(m2m_changed, sender=Profile)
def new_follower(sender, **kwargs):
    if kwargs['action'] == "post_add" and not kwargs['reverse']:
        to_user = kwargs['instance'].user
        new_followers = kwargs['pk_set']
        new_followers = [Notification(
            user=to_user, sender=User.objects.get(id=follower),
            text=f"{User.objects.get(id=follower)} has started following you"
        ) for follower in new_followers]
        Notification.objects.bulk_create(new_followers)


@receiver(m2m_changed, sender=Profile)
def remove_follower(sender, instance, **kwargs):
    if kwargs['action'] == "post_remove":
        followers = kwargs['pk_set']
        for follower in followers:
            notify = Notification.objects.filter(
                sender=User.objects.get(id=follower), user=instance.user)
            notify.delete()
