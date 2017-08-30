import logging

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from files.models import File
from .models import Torrent
from .tasks import update_and_save_information

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Torrent)
def apply_async_update_and_save_information(**kwargs):
    """
    Calls update_and_save_information task right torrent created.
    """
    if kwargs['created']:
        update_and_save_information.delay(kwargs['instance'])


@receiver(m2m_changed, sender=Torrent.files.through)
def link_to_users(**kwargs):
    """
    Links files of the torrent to the users which are related to the torrent.
    Sorry for my bed england if it's not clear; literally it will run right after
    the `torrent.files.add(*files)` operation.
    """
    if kwargs['action'] == 'post_add':
        files = File.objects.filter(pk__in=kwargs['pk_set'])

        for user in kwargs['instance'].user_set.all().iterator():
            user.files.add(*files)
            logger.info('{} linked to {}'.format(list(files), user))
