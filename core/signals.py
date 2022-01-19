import profile
from urllib import request
from django.db.models.signals import m2m_changed, post_save
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

@receiver(post_save, sender=Profile)
def defaultProfileImage(sender, instance, **kwargs):
    DEFAULT = "https://firebasestorage.googleapis.com/v0/b/connect-dac36.appspot.com/o/images%2Ff7bdfca0-b8d2-4c1e-b686-1a8e9465d437?alt=media&token=ec3d49f5-402c-40fb-abc4-0f3616eb0ac4"
    if instance.profile_photo is None:
        instance.profile_photo = DEFAULT
        instance.save()
