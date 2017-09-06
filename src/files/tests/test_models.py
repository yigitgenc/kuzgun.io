import os
import time

from django.test import TestCase

from ..enums import Volume
from ..models import File


class FileModelTests(TestCase):
    """
    Unit tests for File model.
    """
    def test_init_model_without_params(self):
        f = File()

        self.assertEqual(f.name, '')
        self.assertEqual(f.ext, '')
        self.assertEqual(f.full_path, '')
        self.assertIsNone(f.content_type)
        self.assertEqual(f.size, 0)

    def test_create_object_with_volume_and_path(self):
        name = '{}-sample'.format(int(time.time()))
        avi_file = open('/{}/.test/{}.avi'.format(Volume.TORRENT.value, name), 'w+')

        f = File.objects.create(volume=Volume.TORRENT, path='.test/{}.avi'.format(name))

        self.assertEqual(f.name, name)
        self.assertEqual(f.ext, 'avi')
        self.assertEqual(f.full_path, '/{}/.test/{}.avi'.format(Volume.TORRENT.value, name))
        self.assertEqual(f.content_type, 'video/x-msvideo')
        self.assertIs(f.size, 0)
        self.assertEqual(f.file_name, '{}.avi'.format(name))
        self.assertFalse(f.mp4_status)
        self.assertTrue(f.exists_on_disk())
        self.assertEqual(repr(f), '<File: {} (#{})>'.format(f.file_name, f.pk))

        avi_file.close()
        os.remove('/{}/.test/{}.avi'.format(Volume.TORRENT.value, name))

    def test_create_object_with_volume_and_path_but_non_exist(self):
        f = File.objects.create(volume=Volume.TORRENT, path='cr#zy ass\ "f!l3$#!%@.dat.txt')

        self.assertEqual(f.name, 'cr#zy ass\ "f!l3$#!%@.dat')
        self.assertEqual(f.ext, 'txt')
        self.assertEqual(f.full_path, '/{}/cr#zy ass\ "f!l3$#!%@.dat.txt'.format(Volume.TORRENT.value))
        self.assertEqual(f.content_type, 'text/plain')
        self.assertIs(f.size, 0)
        self.assertEqual(f.file_name, 'cr#zy ass\ "f!l3$#!%@.dat.txt')
        self.assertFalse(f.exists_on_disk())
        self.assertFalse(f.mp4_status)

    def test_create_object_sized_zero_and_set_size(self):
        name = '{}-sample'.format(int(time.time()))
        txt_file = open('/{}/.test/{}.txt'.format(Volume.TORRENT.value, name), 'w+')

        f = File.objects.create(volume=Volume.TORRENT, path='.test/{}.txt'.format(name))

        f.set_size()

        self.assertIs(f.size, 0)

        txt_file.write('increase the size please.')
        txt_file.close()

        f.set_size()

        self.assertGreater(f.size, 0)
        os.remove('/{}/.test/{}.txt'.format(Volume.TORRENT.value, name))
