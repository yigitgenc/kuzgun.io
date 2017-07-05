from rest_framework import serializers

from kuzgun.utils import enum_to_dict, redis
from files.serializers import FileSerializer
from .models import Torrent


class TorrentSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    rate_upload = serializers.SerializerMethodField()
    rate_download = serializers.SerializerMethodField()
    files = FileSerializer(read_only=True, many=True)

    class Meta:
        model = Torrent
        fields = '__all__'

    def get_status(self, obj):
        return enum_to_dict(obj.status)

    def get_rate_upload(self, obj):
        return int(redis.hget('torrent:{}'.format(obj.pk), 'rate_upload') or 0)

    def get_rate_download(self, obj):
        return int(redis.hget('torrent:{}'.format(obj.pk), 'rate_download') or 0)
