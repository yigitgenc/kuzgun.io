from hashlib import sha1

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import http_date
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework_extensions.mixins import NestedViewSetMixin

from kuzgun.utils import unix_time_millis, redis
from torrents.models import Torrent
from .enums import Volume
from .models import File, FILE_HASH
from .tasks import convert_to_mp4
from .serializers import FileSerializer

VIDEO_EXTENSIONS = ('mkv', 'avi', 'mov', 'flv', 'wmv', 'mpg')


class FileViewSet(NestedViewSetMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    @staticmethod
    def _parent_lookup(parent_lookup_torrent):
        if parent_lookup_torrent:
            torrent_model = get_object_or_404(Torrent, pk=parent_lookup_torrent)

            if not torrent_model.finished:
                return Response({
                    'detail': "The torrent hasn't finished downloading yet.",
                    'progress': torrent_model.progress
                }, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return self.request.user.files.all()

    def list(self, request, parent_lookup_torrent=None, *args, **kwargs):
        parent_lookup = self._parent_lookup(parent_lookup_torrent)

        if parent_lookup:
            return parent_lookup

        return super(FileViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, parent_lookup_torrent=None, *args, **kwargs):
        parent_lookup = self._parent_lookup(parent_lookup_torrent)

        if parent_lookup:
            return parent_lookup

        return super(FileViewSet, self).retrieve(request, *args, **kwargs)

    @detail_route()
    def convert(self, request, parent_lookup_torrent=None, pk=None):
        parent_lookup = self._parent_lookup(parent_lookup_torrent)

        if parent_lookup:
            return parent_lookup

        obj = self.get_object()

        if obj.ext not in VIDEO_EXTENSIONS:
            return Response({'detail': "Conversion not available for this file."}, status=status.HTTP_400_BAD_REQUEST)

        if redis.hget(FILE_HASH.format(obj.pk), 'conversion_started'):
            return Response({'detail': "Conversion already started."})

        obj_mp4 = File.objects.filter(volume=obj.volume, name=obj.name, ext='mp4').first()

        if obj_mp4 and obj_mp4.mp4_status:
            if obj_mp4.mp4_status['progress'] != '100.00':
                return Response({
                    'detail': "Conversion in progress.",
                    'progress': obj_mp4.mp4_status['progress']
                }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'detail': "Conversion was completed.",
                'progress': '100.00'
            }, status=status.HTTP_400_BAD_REQUEST)
        elif obj_mp4:
            return Response({
                'detail': "There is already a MP4 version of this file."
            }, status=status.HTTP_400_BAD_REQUEST)

        if obj.volume == Volume.TORRENT:
            convert_to_mp4.delay(obj.pk, torrent_ids=list(obj.torrent_set.values_list('pk', flat=True)))
        else:
            convert_to_mp4.delay(obj.pk)

        redis.hset(FILE_HASH.format(obj.pk), 'conversion_started', True)

        return Response({'detail': "Conversion has started."})

    @detail_route()
    def download(self, request, parent_lookup_torrent=None, pk=None):
        parent_lookup = self._parent_lookup(parent_lookup_torrent)

        if parent_lookup:
            return parent_lookup

        obj = self.get_object()

        if obj.ext == 'mp4' and obj.mp4_status and obj.mp4_status['progress'] != '100.00':
            return Response({
                'detail': "{} hasn't completely converted yet.".format(obj.file_name),
                'progress': obj.mp4_status['progress']
            }, status=status.HTTP_400_BAD_REQUEST)

        response = HttpResponse(content_type=obj.content_type, status=status.HTTP_206_PARTIAL_CONTENT)

        response['X-Accel-Redirect'] = '/protected_files/{}?filename={}&last_modified={}&etag={}&start={}'.format(
            obj.path,
            obj.file_name,
            http_date(unix_time_millis(obj.created)),
            sha1(obj.file_name.encode('utf-8')).hexdigest(),
            request.query_params.get('start')
        )

        response['Content-Disposition'] = "attachment; filename={}".format(obj.file_name)
        response['Content-Length'] = obj.size

        return response
