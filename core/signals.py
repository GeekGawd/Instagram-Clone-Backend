import profile
from urllib import request
from django.db.models.signals import m2m_changed, post_save, post_init, post_delete
from django.dispatch import receiver
from rest_framework.response import Response
from core.models import Notification, User
from socialuser.models import Comment, Post, Profile
from chat.models import Message


@receiver(m2m_changed, sender=Profile)
def new_follower(sender, **kwargs):
    if kwargs['action'] == "post_add" and not kwargs['reverse']:
        to_user = kwargs['instance'].user
        new_followers = kwargs['pk_set']
        new_followers = [Notification(
            user=to_user, sender=User.objects.get(id=follower),
            text=f"{User.objects.get(id=follower)} has started following you", noti_type=1
        ) for follower in new_followers]
        Notification.objects.bulk_create(new_followers)


@receiver(m2m_changed, sender=Profile)
def remove_follower(sender, instance, **kwargs):
    if kwargs['action'] == "post_remove":
        followers = kwargs['pk_set']
        for follower in followers:
            notify = Notification.objects.filter(
                sender=User.objects.get(id=follower), user=instance.user, noti_type=1)
            notify.delete()

# @receiver(post_save, sender=Profile)
# def defaultProfileImage(sender, instance, **kwargs):
#     DEFAULT = "https://firebasestorage.googleapis.com/v0/b/connect-dac36.appspot.com/o/images%2Ff7bdfca0-b8d2-4c1e-b686-1a8e9465d437?alt=media&token=ec3d49f5-402c-40fb-abc4-0f3616eb0ac4"
#     if instance.profile_photo is None:
#         instance.profile_photo = DEFAULT
#         instance.save()

@receiver(post_init, sender=Comment)
def commentNotification(sender,instance, **kwargs):
    comment = instance.content
    comment_by_profile = Profile.objects.get(user=instance.comment_by)
    post = instance.post
    if post:
        if post.user != comment_by_profile.user:
            Notification.objects.create(post=post,sender=comment_by_profile.user,
                                        text=f"{comment_by_profile.username} has commented on your post: {comment[:100]}",
                                        user=post.user, noti_type=2)

@receiver(post_delete, sender=Comment)
def deleteCommentNotification(sender,instance, **kwargs):
    comment = instance.content
    comment_by = instance.comment_by
    post = instance.post
    notification = Notification.objects.filter(post=post,sender=comment_by.id,
                                        user=post.user,noti_type=2)
    notification.delete()

@receiver(m2m_changed, sender=Post.liked_by.through)
def likeNotification(sender,**kwargs):
    if kwargs['action'] == "post_add" and not kwargs['reverse']:
        post = kwargs['instance']
        to_user = post.user
        liked_by_users = kwargs['pk_set']
        like_notification = [Notification(
            post=post,
            user=to_user, sender=User.objects.get(id=user),
            text=f"{User.objects.get(id=user).profile.username} liked your post.", noti_type=3
        ) for user in liked_by_users]
        Notification.objects.bulk_create(like_notification)

@receiver(m2m_changed, sender=Post.liked_by.through)
def removelikeNotification(sender,instance, **kwargs):
    if kwargs['action'] == "post_remove" and not kwargs['reverse']:
        liked_by_users = kwargs['pk_set']
        for user_id in liked_by_users:
            notify = Notification.objects.filter(
                sender=User.objects.get(id=user_id), user=instance.user, noti_type=3)
            notify.delete()