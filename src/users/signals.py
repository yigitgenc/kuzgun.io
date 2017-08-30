from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=get_user_model())
def create_auth_token(**kwargs):
    """
    Creates token object right after User object created.
    """
    if kwargs['created']:
        Token.objects.create(user=kwargs['instance'])
