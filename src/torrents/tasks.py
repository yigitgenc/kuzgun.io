from celery.utils.log import get_task_logger
from django.db.models import Sum
from django.utils import timezone

from kuzgun.celery import app
from kuzgun.utils import redis
from files.utils import create_from_torrent
from .enums import Status
from .utils import transmission

COUNTDOWN = 5  # seconds
logger = get_task_logger(__name__)


@app.task(bind=True, serializer='pickle')
def update_and_stop_seeding(self, torrent_model):
    """
    Checks the Torrent object every COUNTDOWN seconds and
    stops the torrent from seeding if it's seeded more than 24 hours.

    :param self: instance of @app.task
    :param torrent_model: Torrent object
    :return: None|AsyncResult
    """
    past = timezone.now() + timezone.timedelta(hours=-24)
    torrent = transmission.get_torrent(torrent_model.hash)

    if torrent_model.created < past:
        torrent_model.ratio = torrent.ratio
        torrent_model.status = Status.STOPPED
        torrent_model.save()
        torrent.stop()

        redis.hset('torrent:{}'.format(torrent_model.pk), 'rate_upload', 0)

        logger.info('{} stopped seeding.'.format(torrent_model))

        return

    redis.hset('torrent:{}'.format(torrent_model.pk), 'rate_upload', torrent.rateUpload)

    torrent_model.status = Status(torrent.status)
    torrent_model.ratio = torrent.ratio
    torrent_model.save()

    return self.apply_async((torrent_model,), countdown=COUNTDOWN)


@app.task(bind=True, serializer='pickle')
def update_and_save_information(self, torrent_model):
    """
    Updates the Torrent object every COUNTDOWN seconds and stops
    when the torrent finishes downloading.

    :param self: instance of @app.task
    :param torrent_model: Torrent object
    :return: None|AsyncResult
    """
    torrent = transmission.get_torrent(torrent_model.hash)

    torrent_model.status = Status(torrent.status)
    torrent_model.progress = torrent.progress
    torrent_model.ratio = torrent.ratio

    redis.hset('torrent:{}'.format(torrent_model.pk), 'rate_upload', torrent.rateUpload)
    redis.hset('torrent:{}'.format(torrent_model.pk), 'rate_download', torrent.rateDownload)

    if int(torrent_model.progress) != 100:
        torrent_model.save()
        return self.apply_async((torrent_model,), countdown=COUNTDOWN)

    files = create_from_torrent(torrent)
    torrent_model.files.add(*files)

    torrent_model.finished = True
    torrent_model.progress = 100
    torrent_model.size = torrent_model.files.all().aggregate(Sum('size')).get('size__sum', 0)
    torrent_model.save()

    redis.hmset('torrent:{}'.format(torrent_model.pk), {
        'rate_upload': 0,
        'rate_download': 0,
    })

    logger.info('{} finished downloading.'.format(torrent_model))

    update_and_stop_seeding.delay(torrent_model)

    return
