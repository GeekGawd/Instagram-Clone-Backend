from urllib import request
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from core.models import Notification, User


# @receiver(m2m_changed)
# def new_follower(sender, **kwargs):
#     if kwargs['action'] == "post_add" and not kwargs['reverse']:
#         to_user = kwargs['instance'].user
#         new_followers = kwargs['pk_set']
#         new_followers = [Notification(
#             user=to_user, sender=follower,
#             text=f"{follower} has started following you"
#             ) for follower in new_followers]
#         Notification.objects.bulk_create(new_followers)

# def remove_follower(sender,instance,**kwargs):
#     pass
#     # if kwargs['action'] == "post_add" and not kwargs['reverse']:
#     #     profile = instance
#     #     sender = profile.follower
#     #     following = follow.following

#     #     notify = Notification.objects.filter(sender=sender, user=following, notification_type=3)
#     #     notify.delete()
