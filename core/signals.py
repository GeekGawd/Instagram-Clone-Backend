from django.db.models.signals import m2m_changed
from django.dispatch import receiver

@receiver(m2m_changed)
def new_follower(sender, **kwargs):
    if kwargs['action'] == "post_add":
        print("Someone has started following you")
