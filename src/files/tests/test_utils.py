from unittest.mock import patch

from django.test import TestCase

from files.models import File
from ..utils import create_from_torrent


class FileUtilTests(TestCase):
    """
    Unit tests for file utils.
    """
    @patch('torrents.utils.transmission')
    def test_create_from_torrent(self, mock_instance):
        mock_instance.files.return_value = {
            0: {
                'name': 'The.Quick.Brown/The quick brown fox jumps over the lazy dog.jpg',
                'size': 8827
            },
            1: {
                'name': 'The.Quick.Brown/The quick brown fox jumps over the lazy dog.avi',
                'size': 2802579083
            }
        }

        files = create_from_torrent(mock_instance)

        self.assertIs(type(files), set)
        self.assertGreater(len(files), 0)

        for file in files:
            self.assertIsInstance(file, File)
