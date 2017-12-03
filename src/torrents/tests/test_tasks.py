from collections import namedtuple
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from files.enums import Volume
from files.models import File
from ..models import Torrent, TORRENT_HASH
from ..tasks import update_and_save_information, update_and_stop_seeding, COUNTDOWN


def mock_stop():
    pass


class TorrentTaskTest(TestCase):
    """
    Unit tests for torrent tasks.
    """
    def setUp(self):
        self.file = File.objects.create(volume=Volume.DATA, path='drop.avi')
        self.file_mp4 = File.objects.create(volume=Volume.DATA, path='drop.mp4')
        self.torrent = namedtuple('torrent', ['status', 'progress', 'ratio', 'rateUpload', 'rateDownload', 'stop'])
        self.torrent_model = Torrent.objects.create(
            hash='63b024bf50a50ca95f1b2364a946faf8',
            name='sample.avi'
        )

    def _apply_common_assertions(self, mock_get_torrent, mock_hmset):
        mock_get_torrent.assert_called_with(self.torrent_model.hash)
        self.assertTrue(mock_hmset.has_called_with(TORRENT_HASH.format(self.torrent_model.pk), {
            'rate_upload': mock_get_torrent.rateUpload,
            'rate_download': mock_get_torrent.rateDownload
        }))

    def test_update_and_save_information_that_except_does_not_exist(self):
        torrent_id = 99999
        result = update_and_save_information(torrent_id)

        self.assertIsNone(result)

    @patch('torrents.tasks.update_and_save_information.apply_async')
    @patch('torrents.tasks.redis.hmset')
    @patch('torrents.tasks.transmission.get_torrent')
    def test_update_and_save_information_that_return_apply_async(self, mock_get_torrent, mock_hmset, mock_apply_async):
        mock_get_torrent.return_value = self.torrent(
            status='downloading',
            progress=Decimal('45.97'),
            ratio=Decimal('9.99'),
            rateUpload=10500,
            rateDownload=105000,
            stop=None
        )

        update_and_save_information(self.torrent_model.pk)

        self._apply_common_assertions(mock_get_torrent, mock_hmset)
        mock_get_torrent.assert_called_with(self.torrent_model.hash)
        mock_apply_async.assert_called_with((self.torrent_model.pk,), countdown=COUNTDOWN)

    @patch('torrents.tasks.create_from_torrent')
    @patch('torrents.tasks.update_and_stop_seeding.delay')
    @patch('torrents.tasks.redis.hmset')
    @patch('torrents.tasks.transmission.get_torrent')
    def test_update_and_save_information_that_return_none(
            self, mock_get_torrent, mock_hmset,
            mock_update_and_stop_seeding_delay,
            mock_create_from_torrent
    ):
        mock_create_from_torrent.return_value = (self.file, self.file_mp4)

        mock_get_torrent.return_value = self.torrent(
            status='downloading',
            progress=Decimal('100.00'),
            ratio=Decimal('9.99'),
            rateUpload=10500,
            rateDownload=105000,
            stop=None
        )

        update_and_save_information(self.torrent_model.pk)

        self._apply_common_assertions(mock_get_torrent, mock_hmset)
        mock_get_torrent.assert_called_with(self.torrent_model.hash)
        mock_update_and_stop_seeding_delay.assert_called_with(self.torrent_model.pk)

    def test_update_and_stop_seeding_that_except_does_not_exist(self):
        torrent_id = 99999
        result = update_and_stop_seeding(torrent_id)

        self.assertIsNone(result)

    @patch('torrents.tasks.update_and_stop_seeding.apply_async')
    @patch('torrents.tasks.redis.hset')
    @patch('torrents.tasks.transmission.get_torrent')
    def test_update_and_stop_seeding_that_return_apply_async(self, mock_get_torrent, mock_hset, mock_apply_async):
        mock_get_torrent.return_value = self.torrent(
            status='downloading',
            progress=Decimal('100.00'),
            ratio=Decimal('9.99'),
            rateUpload=10500,
            rateDownload=105000,
            stop=None
        )

        update_and_stop_seeding(self.torrent_model.pk)

        mock_get_torrent.assert_called_with(self.torrent_model.hash)
        mock_hset.assert_called_with(
            'torrent:{}'.format(self.torrent_model.pk), 'rate_upload', mock_get_torrent.return_value.rateUpload
        )
        mock_apply_async.assert_called_with((self.torrent_model.pk,), countdown=COUNTDOWN)

    @patch('torrents.tasks.redis.hset')
    @patch('torrents.tasks.transmission.get_torrent')
    def test_update_and_stop_seeding_that_stopped_return_none(self, mock_get_torrent, mock_hset):
        mock_get_torrent.return_value = self.torrent(
            status='stopped',
            progress=Decimal('100.00'),
            ratio=Decimal('9.99'),
            rateUpload=10500,
            rateDownload=105000,
            stop=mock_stop
        )

        self.assertIsNone(update_and_stop_seeding(self.torrent_model.pk))

        mock_get_torrent.assert_called_with(self.torrent_model.hash)
        mock_hset.assert_called_with(
            'torrent:{}'.format(self.torrent_model.pk), 'rate_upload', 0
        )

    @patch('torrents.tasks.redis.hset')
    @patch('torrents.tasks.transmission.get_torrent')
    def test_update_and_stop_seeding_that_seeding_return_none(self, mock_get_torrent, mock_hset):
        mock_get_torrent.return_value = self.torrent(
            status='seeding',
            progress=Decimal('100.00'),
            ratio=Decimal('9.99'),
            rateUpload=10500,
            rateDownload=105000,
            stop=mock_stop
        )

        self.torrent_model.created = timezone.now() + timezone.timedelta(hours=-24, seconds=-1)
        self.torrent_model.save()

        self.assertIsNone(update_and_stop_seeding(self.torrent_model.pk))

        mock_get_torrent.assert_called_with(self.torrent_model.hash)
        mock_hset.assert_called_with('torrent:{}'.format(self.torrent_model.pk), 'rate_upload', 0)
