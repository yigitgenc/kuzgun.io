from .models import File
from .enums import Volume


def create_from_torrent(torrent):
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
