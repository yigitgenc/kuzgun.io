from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from torrents.models import Torrent
from ..enums import Volume
from ..models import File, FILE_HASH


class FileViewSetTests(APITestCase):
    """
    Unit tests File API endpoint.
    """
    def setUp(self):
        self.user = get_user_model().objects.create_user('johndoe', 'john@doe.com', 'johndoe')
        self.client.login(username='johndoe', password='johndoe')

        self.torrent = Torrent.objects.create(
            hash='63b024bf50a50ca95f1b2364a946faf8',
            name='sample.avi',
            private=False,
            progress=Decimal('3.93')
        )

        self.file = File.objects.create(volume=Volume.TORRENT, path='.test/drop.avi')
        self.file_mp4 = File.objects.create(volume=Volume.TORRENT, path='.test/drop.mp4')

        self.user.torrents.add(self.torrent)
        self.torrent.files.add(self.file, self.file_mp4)

    def test_retrieve_file(self):
        url = reverse('files:file-detail', args=[self.file.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_torrent_file_that_return_has_not_finished_downloading(self):
        url = reverse('torrents:torrent-file-detail', args=[self.torrent.pk, self.file.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('detail'), "The torrent hasn't finished downloading yet.")
        self.assertEqual(response.data.get('progress'), Decimal('3.93'))

    def test_list_files(self):
        url = reverse('files:file-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('count'))
        self.assertIsNotNone(response.data.get('results'))

    def test_convert_endpoint_that_return_not_available(self):
        file = File.objects.create(volume=Volume.TORRENT, path='.test/sample.txt')
        self.user.files.add(file)

        url = reverse('files:file-convert', args=[file.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('detail'), 'Conversion not available for this file.')

    @patch('files.views.redis.hget')
    def test_convert_endpoint_that_return_already_started(self, mock_hget):
        url = reverse('files:file-convert', args=[self.file.pk])

        mock_hget.return_value = True
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('detail'), 'Conversion already started.')

    @patch('files.models.redis.hgetall')
    @patch('files.models.redis.hget')
    def test_convert_endpoint_that_return_already_in_progress(self, mock_hget, mock_hgetall):
        url = reverse('files:file-convert', args=[self.file.pk])

        mock_hget.return_value = False
        mock_hgetall.return_value = {
            'duration': 6,
            'progress': '78.53'
        }

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('detail'), 'Conversion in progress.')
        self.assertEqual(response.data.get('progress'), '78.53')

    @patch('files.models.redis.hgetall')
    @patch('files.models.redis.hget')
    def test_convert_endpoint_that_return_already_have(self, mock_hget, mock_hgetall):
        url = reverse('files:file-convert', args=[self.file.pk])

        mock_hget.return_value = False
        mock_hgetall.return_value = False

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('detail'), 'There is already a MP4 version of this file.')

    @patch('files.models.redis.hgetall')
    @patch('files.models.redis.hget')
    def test_convert_endpoint_that_return_completed(self, mock_hget, mock_hgetall):
        url = reverse('files:file-convert', args=[self.file.pk])

        mock_hget.return_value = False
        mock_hgetall.return_value = {
            'duration': 6,
            'progress': '100.00'
        }

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('detail'), 'Conversion was completed.')
        self.assertEqual(response.data.get('progress'), '100.00')

    @patch('files.views.convert_to_mp4.delay')
    @patch('files.views.redis.hset')
    @patch('files.views.redis.hget')
    def test_convert_endpoint_that_return_success(self, mock_hget, mock_hset, mock_convert_to_mp4_delay):
        self.file_mp4.delete()

        mock_hget.return_value = False

        url = reverse('files:file-convert', args=[self.file.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('detail'), 'Conversion has started.')

        mock_convert_to_mp4_delay.assert_called_with(
            self.file.pk, torrent_ids=list(self.file.torrent_set.values_list('pk', flat=True))
        )
        mock_hset.assert_called_with(FILE_HASH.format(self.file.pk), 'conversion_started', True)

    @patch('files.models.redis.hgetall')
    def test_download_endpoint_that_return_in_progress(self, mock_hgetall):
        url = reverse('files:file-download', args=[self.file_mp4.pk])
        mock_hgetall.return_value = {
            'duration': 6,
            'progress': '98.11'
        }

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data.get('detail'), "{} hasn't completely converted yet.".format(self.file_mp4.file_name)
        )
        self.assertEqual(response.data.get('progress'), '98.11')

    def test_download_endpoint_that_return_partial_content(self):
        url = reverse('files:file-download', args=[self.file.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_206_PARTIAL_CONTENT)
        self.assertEqual(
            response._headers['content-disposition'][1], "attachment; filename={}".format(self.file.file_name)
        )
        self.assertEqual(response._headers['content-length'][1], str(self.file.size))
