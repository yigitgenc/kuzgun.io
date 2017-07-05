from enumfields.enums import Enum


class Volume(Enum):
    UPLOAD = 'uploads'
    DOWNLOAD = 'downloads'
    TORRENT = 'torrents/complete'

    class Labels:
        UPLOAD = 'Upload'
        DOWNLOAD = 'Download'
        TORRENT = 'Torrent'
