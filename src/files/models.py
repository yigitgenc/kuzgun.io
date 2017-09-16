import os
import logging
import mimetypes

from django.db import models
from django_extensions.db.models import TimeStampedModel
from enumfields.fields import EnumField

from kuzgun.utils import redis
from .enums import Volume

FILE_HASH = 'file:{}'
MP4_STATUS_HASH = 'file:{}:mp4_status'

logger = logging.getLogger(__name__)


class File(TimeStampedModel):
    """
    File model that keeps files independently.
    Can be linked to Torrent and User through ManyToMany.
    """
    volume = EnumField(Volume, max_length=20)
    path = models.FilePathField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    ext = models.CharField(max_length=5)
    content_type = models.CharField(max_length=20, null=True)
    size = models.BigIntegerField(default=0)

    class Meta:
        ordering = ('-id',)

    def __init__(self, *args, **kwargs):
        """
        Set name, ext and content_type (if possible) automatically initialize by path.
        """
        super(File, self).__init__(*args, **kwargs)
        pieces = os.path.splitext(os.path.basename(str(self.path)))
        self.name, self.ext = pieces[0], pieces[1][1:]
        self.content_type = mimetypes.guess_type(self.full_path)[0]

    def __str__(self):
        return '{} (#{})'.format(self.file_name, self.pk)

    def delete(self, using=None, keep_parents=False):
        try:
            os.remove(self.full_path)
        except FileNotFoundError:
            logger.info(('File {} does not exist. May be force deleted from the storage. '
                         'However {} object is being deleted.').format(
                self.full_path, self.__str__()
            ))

        return super(File, self).delete(using=using, keep_parents=keep_parents)

    @property
    def file_name(self):
        """
        Returns file name.

        :return: str
        """
        return '{}.{}'.format(self.name, self.ext)

    @property
    def full_path(self):
        """
        Returns full path if volume is set.
        Volume control for Django admin (add) to avoid raising exception on init.

        :return: str
        """
        return self.volume and '/{}/{}'.format(self.volume.value, self.path) or ''

    @property
    def mp4_status(self):
        """
        Returns file:{pk}:mp4_status hash from redis if set and a MP4 file.

        :return: dict|bool
        """
        if self.ext != 'mp4':
            return False

        data = redis.hgetall(MP4_STATUS_HASH.format(self.pk))

        return {
            'duration': int(data.get('duration', 0)),
            'progress': data.get('progress', '0.00'),
        } if data else False

    def set_size(self):
        """
        Sets size
        """
        self.size = os.path.getsize(self.full_path)

    def exists_on_disk(self):
        """
        Detect file whether on the disk or not.

        :return: bool
        """
        return os.path.isfile(self.full_path)
