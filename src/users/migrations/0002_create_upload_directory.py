# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.db import migrations

from files.enums import Volume


def create_upload_directory(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    MyUser = apps.get_model('users', 'MyUser')

    for username in MyUser.objects.using(db_alias).values_list('username', flat=True).all().iterator():
        os.mkdir('/{}/{}'.format(Volume.UPLOAD.value, username))


def reverse_create_upload_directory(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    MyUser = apps.get_model('users', 'MyUser')

    for username in MyUser.objects.using(db_alias).values_list('username', flat=True).all().iterator():
        os.rmdir('/{}/{}'.format(Volume.UPLOAD.value, username))


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_upload_directory, reverse_create_upload_directory)
    ]
