import re
import os
import shlex
import time
from fcntl import fcntl, F_GETFL, F_SETFL
from subprocess import Popen, STDOUT, PIPE

from celery.utils.log import get_task_logger

from kuzgun.celery import app
from kuzgun.utils import redis
from torrents.models import Torrent
from .models import File, MP4_STATUS_HASH

logger = get_task_logger(__name__)


@app.task
def convert_to_mp4(file_id, **kwargs):
    """
    This task duplicates File object itself, saves it as MP4 file object with empty size
    and right after opens process to execute ffprobe and ffmpeg. FFprobe gets info so
    we can get the duration. FFmpeg converts given file to MP4. Giving non-blocking
    IO flag to process allowing us to get completed conversion time in seconds.

    :param file_id: int
    :param kwargs: {'torrent_ids': list}
    :return: None
    """
    f = File.objects.get(pk=file_id)
    f_mp4 = File.objects.create(volume=f.volume, path='{}.mp4'.format(os.path.splitext(f.path)[0]))

    if kwargs.get('torrent_ids'):
        for torrent_model in Torrent.objects.filter(pk__in=kwargs['torrent_ids']).iterator():
            torrent_model.files.add(f_mp4)
            torrent_model.save()

    proc = Popen(shlex.split('/usr/bin/ffprobe -i "{}"'.format(
        f.full_path
    )), stderr=STDOUT, stdout=PIPE)

    duration_search = re.search(b'(Duration:)(.|\s|)(\d+):(\d+):(\d+)', proc.communicate()[0])
    hours, minutes, seconds = duration_search.group().split(b': ')[1].split(b':')
    duration = (int(hours) * 3600) + (int(minutes) * 60) + int(seconds)
    redis.hset(MP4_STATUS_HASH.format(f_mp4.pk), 'duration', duration)

    output_options = {
        'mkv': '-vcodec copy -acodec copy -ac 2 -ab 128k -crf 23',
        'avi': '-vcodec libx264 -acodec aac -ac 2 -ab 128k -crf 23'
    }.get(f.ext, '')

    proc = Popen(shlex.split('/usr/bin/ffmpeg -y -i "{}" {} "{}"'.format(
        f.full_path, output_options, f_mp4.full_path
    )), stderr=STDOUT, stdout=PIPE)

    flags = fcntl(proc.stdout, F_GETFL)
    fcntl(proc.stdout, F_SETFL, flags | os.O_NONBLOCK)

    while proc.poll() is None:
        time.sleep(0.25)  # Let's don't upset our CPU. Sleep 250 milliseconds of a second (1/4).
        line = proc.stdout.readline()

        time_search = re.search(b'(time=)(\d+):(\d+):(\d+)', line)

        if time_search:
            hours, minutes, seconds = time_search.group().split(b'=')[1].split(b':')
            time_seconds = (int(hours) * 3600) + (int(minutes) * 60) + int(seconds)
            redis.hset(
                MP4_STATUS_HASH.format(f_mp4.pk), 'progress', '{:.2f}'.format((time_seconds * 100) / duration)
            )

    redis.hset(MP4_STATUS_HASH.format(f_mp4.pk), 'progress', '100.00')

    f_mp4.set_size()
    f_mp4.save()

    logger.info('{} finished converting to MP4.'.format(f))

    return
