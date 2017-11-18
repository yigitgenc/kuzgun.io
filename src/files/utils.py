from .models import File
from .enums import Volume


def create_from_torrent(torrent):
    """
    Creates file objects from transmission torrent object.
    Returns list of file objects so we can use it for something
    different purposes. For example: torrent.files.add(*files)

    :param torrent: Transmission torrent object
    :return: set
    """
    files = set()

    for _, item in torrent.files().items():
        path = item['name']

        f, _ = File.objects.get_or_create(
            volume=Volume.TORRENT,
            path=path,
            defaults={'size': item['size']},
        )

        files.add(f)

    return files


def handle_uploaded_file(uploaded_file_obj, full_path):
    """
    Moves uploaded file object to the destination (full_path).

    :param uploaded_file_obj: InMemoryUploadedFile|UploadedFile object.
    :param full_path: str: Full path of the file object.
    :return: None
    """
    with open(full_path, 'wb+') as destination:
        for chunk in uploaded_file_obj.chunks():
            destination.write(chunk)
