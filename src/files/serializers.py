from rest_framework import serializers

from kuzgun.utils import enum_to_dict
from .models import File


class FileSerializer(serializers.ModelSerializer):
    """
    Serializer class of the File model.
    """
    volume = serializers.SerializerMethodField()
    mp4_status = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = '__all__'

    def get_volume(self, obj):
        """
        Get volume as a dict.

        :param obj: File object
        :return: dict
        """
        return enum_to_dict(obj.volume)

    def get_mp4_status(self, obj):
        """
        Get mp4_status property.

        :param obj: File object
        :return: dict|bool
        """
        return obj.mp4_status
