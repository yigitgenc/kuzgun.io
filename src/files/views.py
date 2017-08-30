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

# Only these video formats can be converted to MP4.
# Current supports: MKV, AVI.
VIDEO_EXTENSIONS = ('mkv', 'avi')


class FileViewSet(NestedViewSetMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """
    File API endpoint for File model. (/files).
    Supported methods: Retrieve, List
    """
    queryset = File.objects.all()
    serializer_class = FileSerializer

    @staticmethod
    def _parent_lookup(parent_lookup_torrent):
        """
        This static method tries to get torrent object if the request was came up
        from parent lookup. (/torrents/) It raises a Http404 exception if it can't
        find the torrent object.

        :param parent_lookup_torrent: int
        :return: Response
        """
        if parent_lookup_torrent:
            torrent_model = get_object_or_404(Torrent, pk=parent_lookup_torrent)

            if not torrent_model.finished:
                return Response({
                    'detail': "The torrent hasn't finished downloading yet.",
                    'progress': torrent_model.progress
                }, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        """
        Gets files queryset of the user.

        :return: QuerySet
        """
        return self.request.user.files.all()

    def list(self, request, parent_lookup_torrent=None, *args, **kwargs):
        """
        Lists files of the user.

        :return: Response
        """
        parent_lookup = self._parent_lookup(parent_lookup_torrent)

        if parent_lookup:
            return parent_lookup

        return super(FileViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, parent_lookup_torrent=None, *args, **kwargs):
        """
        Retrieve a file of the user.

        :return: Response
        """
        parent_lookup = self._parent_lookup(parent_lookup_torrent)

        if parent_lookup:
            return parent_lookup

        return super(FileViewSet, self).retrieve(request, *args, **kwargs)

    @detail_route()
    def convert(self, request, parent_lookup_torrent=None, pk=None):
        """
        Converts given file to MP4. Calls convert_to_mp4 task.
        If extension can't be find in VIDEO_EXTENSIONS, already
        started or in progress; will return (400) bad request.

        :return: Response
        """
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
        """
        Downloads or streams requested video of the file.
        Redirects to protected path of the file over
        Nginx with X-Accel-Redirect header.

        :return: Response
        """
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
