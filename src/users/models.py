from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    """
    MyUser model that extends AbstractUser. Uses Django's built-in auth model.
    Torrent and File objects can be linked to this model through ManyToMany.
    """
    torrents = models.ManyToManyField('torrents.Torrent')
    files = models.ManyToManyField('files.File')

    class Meta:
        verbose_name = 'User'
        default_related_name = 'user_set'

    def __str__(self):
        return '{} <{}>'.format(self.username, self.email)
