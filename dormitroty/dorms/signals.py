from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Bed

@receiver(post_save, sender=Bed)
@receiver(post_delete, sender=Bed)
def update_room_full_status(sender, instance, **kwargs):
    room = instance.room
    room.set_full_true()