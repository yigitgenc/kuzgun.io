from rest_framework import serializers

from kuzgun.utils import enum_to_dict
from .models import File


class FileSerializer(serializers.ModelSerializer):
    volume = serializers.SerializerMethodField()
    mp4_status = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = '__all__'

    def get_volume(self, obj):
        return enum_to_dict(obj.volume)

    def get_mp4_status(self, obj):
        return obj.mp4_status
