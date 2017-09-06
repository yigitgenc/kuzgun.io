from unittest.mock import call, patch

from django.test import TestCase

from torrents.models import Torrent
from ..enums import Volume
from ..models import File, MP4_STATUS_HASH
from ..tasks import convert_to_mp4


class FileTaskTests(TestCase):
    """
    Unit tests for file tasks.
    """
    def _apply_common_assertions(self, mock_hset, mock_redis):
        hgetall_data = {
            'duration': 6,
            'progress': '100.00'
        }

        mock_redis.hgetall.return_value = hgetall_data

        file_mp4 = File.objects.get(volume=Volume.TORRENT, path='.test/drop.mp4')

        mock_hset.assert_has_calls([
            call(MP4_STATUS_HASH.format(file_mp4.pk), 'duration', 6),
            call(MP4_STATUS_HASH.format(file_mp4.pk), 'progress', '100.00')
        ])

        self.assertTrue(file_mp4.exists_on_disk())
        self.assertTrue(file_mp4.mp4_status)
        self.assertDictEqual(file_mp4.mp4_status, hgetall_data)

    @patch('files.models.redis')
    @patch('files.tasks.redis.hset')
    def test_convert_to_mp4(self, mock_hset, mock_redis):
        file = File.objects.create(volume=Volume.TORRENT, path='.test/drop.avi')
        self.assertIsNone(convert_to_mp4(file.pk))
        self._apply_common_assertions(mock_hset, mock_redis)

    @patch('files.models.redis')
    @patch('files.tasks.redis.hset')
    def test_convert_torrent_file_to_mp4(self, mock_hset, mock_redis):
        torrent_model = Torrent.objects.create(
            hash='63b024bf50a50ca95f1b2364a946faf8',
            name='sample.avi',
            private=False
        )

        file = File.objects.create(volume=Volume.TORRENT, path='.test/drop.avi')

        self.assertIsNone(convert_to_mp4(file.pk, torrent_ids=(torrent_model.pk,)))
        self._apply_common_assertions(mock_hset, mock_redis)
