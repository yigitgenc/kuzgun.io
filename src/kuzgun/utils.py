from redis import ConnectionPool, Redis

from django.utils.timezone import datetime
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # This might be useful for overwriting default error messages. :>
        pass

    return response


def enum_to_dict(enum):
    return {
        'label': enum.label,
        'value': enum.value,
    }


def unix_time_millis(dt):
    naive = dt.replace(tzinfo=None)
    epoch = datetime.utcfromtimestamp(0)
    return (naive - epoch).total_seconds()


# Use ConnectionPool in order to set decode_response to True.
redis_pool = ConnectionPool(host='redis', port=6379, db=0, decode_responses=True)
redis = Redis(connection_pool=redis_pool)
