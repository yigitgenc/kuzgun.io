"""
Celery config.
"""


import os

# Broker URL
broker_url = 'amqp://guest:guest@rabbitmq:5672//'

# Timezone
timezone = os.environ.get('TZ', 'GMT')

# Accept content
accept_content = ('application/json',)

# Worker max tasks per child
worker_max_tasks_per_child = 1

# Task serializer
task_serializer = 'json'

# Task ignore result
task_ignore_result = True

# Task routes
task_routes = {
    'torrents.tasks.update_and_save_information': {
        'queue': 'torrents.update_and_save_information',
    },
    'torrents.tasks.update_and_stop_seeding': {
        'queue': 'torrents.update_and_stop_seeding',
    },
    'files.tasks.convert_to_mp4': {
        'queue': 'files.convert_to_mp4',
    },
}
