from collections import namedtuple
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Torrent


class TorrentViewSetTests(APITestCase):
    """
    Unit tests for Torrent API endpoint.
    """
    def setUp(self):
        self.user = get_user_model().objects.create_user('johndoe', 'john@doe.com', 'johndoe')
        self.client.login(username='johndoe', password='johndoe')

    def test_list_torrents(self):
        url = reverse('torrents:torrent-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('count'))
        self.assertIsNotNone(response.data.get('results'))

    @patch('torrents.views.transmission.add_torrent')
    def test_create_torrent(self, mock_add_torrent):
        url = reverse('torrents:api-root')
        link = "http://www.publicdomaintorrents.com/bt/btdownload.php?type=torrent&file=Telephone_Operator.avi.torrent"

        torrent = namedtuple('torrent', ['hashString', 'name', 'isPrivate'])
        mock_add_torrent.return_value = torrent(
            hashString='fe8d8df9b015e44eccf5f58b210095ea9e0a046d',
            name='Telephone_Operator.avi',
            isPrivate=False
        )

        response = self.client.post(url, {'link': link})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_torrent_that_return_bad_request(self):
        url = reverse('torrents:api-root')
        link = "http://www.publicdomaintorrents.com/bt/btdownload.php?type=torrent&file=Telephone_Operator.avi"

        response = self.client.post(url, {'link': link})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_destroy_torrent(self):
        torrent_model = Torrent.objects.create(hash='63b024bf50a50ca95f1b2364a946faf8', name='sample.avi')
        self.user.torrents.add(torrent_model)

        url = reverse('torrents:torrent-detail', args=[torrent_model.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Torrent.DoesNotExist):
            self.user.torrents.get(pk=torrent_model.pk)
