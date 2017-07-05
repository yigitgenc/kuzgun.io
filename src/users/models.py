from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    torrents = models.ManyToManyField('torrents.Torrent')
    files = models.ManyToManyField('files.File')

    class Meta:
        verbose_name = 'User'
        default_related_name = 'user_set'

    def __str__(self):
        return '{} <{}>'.format(self.username, self.email)
