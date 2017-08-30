from enumfields.enums import Enum


class Status(Enum):
    """
    It specifies status of the transmission torrent object.
    """
    IN_QUEUE = 'in queue'
    CHECK_PENDING = 'check pending'
    CHECKING = 'checking'
    DOWNLOADING = 'downloading'
    SEEDING = 'seeding'
    STOPPED = 'stopped'

    class Labels:
        IN_QUEUE = 'In Queue'
        CHECK_PENDING = 'Pending'
        CHECKING = 'Checking'
        DOWNLOADING = 'Downloading'
        SEEDING = 'Seeding'
        STOPPED = 'Stopped'
