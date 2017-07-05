import os
import mimetypes

from django.db import models
from django_extensions.db.models import TimeStampedModel
from enumfields.fields import EnumField

from kuzgun.utils import redis
from .enums import Volume

FILE_HASH = 'file:{}'
MP4_STATUS_HASH = 'file:{}:mp4_status'


class File(TimeStampedModel):
    volume = EnumField(Volume, max_length=20)
    path = models.FilePathField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    ext = models.CharField(max_length=5)
    content_type = models.CharField(max_length=20, null=True)
    size = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('-id',)

    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        pieces = os.path.splitext(os.path.basename(str(self.path)))
        self.name, self.ext = pieces[0], pieces[1][1:]
        self.content_type = mimetypes.guess_type(self.full_path)[0]

    def __str__(self):
        return '{} (#{})'.format(self.file_name, self.pk)

    @property
    def file_name(self):
        return '{}.{}'.format(self.name, self.ext)

    @property
    def full_path(self):
        return self.volume and '/{}/{}'.format(self.volume.value, self.path) or ''

    @property
    def mp4_status(self):
        if self.ext != 'mp4':
            return False

        data = redis.hgetall(MP4_STATUS_HASH.format(self.pk))

        return {
            'duration': int(data.get('duration', 0)),
            'progress': data.get('progress', '0.00'),
        } if data else False

    def set_content_type(self):
        self.content_type = mimetypes.guess_type(self.full_path)

    def set_size(self):
        self.size = os.path.getsize(self.full_path)
