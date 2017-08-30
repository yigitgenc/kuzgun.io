from enumfields.enums import Enum


class Volume(Enum):
    """
    It specifies a File object which docker volume stored in.
    """
    UPLOAD = 'uploads'
    DOWNLOAD = 'downloads'
    TORRENT = 'torrents/complete'

    class Labels:
        UPLOAD = 'Upload'
        DOWNLOAD = 'Download'
        TORRENT = 'Torrent'
