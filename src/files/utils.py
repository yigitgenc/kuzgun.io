from .models import File
from .enums import Volume


def create_from_torrent(torrent):
    """
    Creates file objects from transmission torrent object.
    Returns list of file objects so we can use it for something
    different purposes. For example: torrent.files.add(*files)

    :param torrent: Transmission torrent object
    :return: list
    """
    files = list()

    for _, item in torrent.files().items():
        path = item['name']

        f, _ = File.objects.get_or_create(
            volume=Volume.TORRENT,
            path=path,
            defaults={'size': item['size']},
        )

        files.append(f)

    return files
