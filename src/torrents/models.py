from decimal import Decimal

from django.db import models
from django_extensions.db.models import TimeStampedModel
from enumfields.fields import EnumField

from .enums import Status


class Torrent(TimeStampedModel):
    name = models.CharField(max_length=150)
    hash = models.CharField(max_length=40, unique=True, db_index=True)
    status = EnumField(Status, max_length=20, default=Status.IN_QUEUE)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ratio = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    size = models.PositiveIntegerField(default=0)
    files = models.ManyToManyField('files.File')
    finished = models.BooleanField(default=False)
    private = models.BooleanField(default=False)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return '{} <{}>'.format(self.name, self.hash)

    def save(self, **kwargs):
        self.progress = Decimal('{:.2f}'.format(self.progress))
        self.ratio = Decimal('{:.2f}'.format(self.ratio))

        return super(Torrent, self).save(**kwargs)
