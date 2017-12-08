import os
from hashlib import sha1

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.http import http_date
from django.utils.text import slugify
from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.parsers import FileUploadParser
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
from .utils import handle_uploaded_file

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
    parser_classes = (FileUploadParser,)

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

        if parent_lookup_torrent:
            # List files of the torrent.
            torrent = get_object_or_404(Torrent, pk=parent_lookup_torrent)
            serializer = self.serializer_class(torrent.files.all(), many=True)

            return Response(serializer.data)

        return super(FileViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, parent_lookup_torrent=None, *args, **kwargs):
        """
        Retrieve a file of the user.

        :return: Response
        """

        if parent_lookup_torrent:
            # Retrieve a file of the torrent.
            torrent = get_object_or_404(Torrent, pk=parent_lookup_torrent)
            if not torrent.finished:
                return Response({
                    'detail': "The torrent hasn't finished downloading yet.",
                    'progress': torrent.progress
                }, status=status.HTTP_400_BAD_REQUEST)

            file_obj = get_object_or_404(File, torrent__pk=parent_lookup_torrent, pk=kwargs.get('pk'))
            serializer = self.serializer_class(file_obj)

            return Response(serializer.data)

        return super(FileViewSet, self).retrieve(request, *args, **kwargs)

    @detail_route()
    def convert(self, request, parent_lookup_torrent=None, pk=None):
        """
        Converts given file to MP4. Calls convert_to_mp4 task.
        If extension can't be find in VIDEO_EXTENSIONS, already
        started or in progress; will return (400) bad request.

        :return: Response
        """

        if parent_lookup_torrent:
            torrent = get_object_or_404(Torrent, pk=parent_lookup_torrent)
            if not torrent.finished:
                return Response({
                    'detail': "The torrent hasn't finished downloading yet.",
                    'progress': torrent.progress
                }, status=status.HTTP_400_BAD_REQUEST)

        obj = self.get_object()

        if obj.ext not in VIDEO_EXTENSIONS:
            return Response({'detail': "Conversion not available for this file."}, status=status.HTTP_400_BAD_REQUEST)

        if redis.hget(FILE_HASH.format(obj.pk), 'conversion_started'):
            return Response({'detail': "Conversion already started."}, status=status.HTTP_400_BAD_REQUEST)

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

        if obj.volume in (Volume.TORRENT, Volume.DATA):
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

        if parent_lookup_torrent:
            torrent = get_object_or_404(Torrent, pk=parent_lookup_torrent)
            if not torrent.finished:
                return Response({
                    'detail': "The torrent hasn't finished downloading yet.",
                    'progress': torrent.progress
                }, status=status.HTTP_400_BAD_REQUEST)

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

    @list_route(['post'])
    def upload(self, request, parent_lookup_torrent=None):
        """
        Handles sent file, creates File object,
        chunks and writes it into Volume.UPLOAD.

        :return: Response
        """

        if parent_lookup_torrent:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        uploaded_file_obj = request.data['file']
        uploaded_file_name, uploaded_file_ext = os.path.splitext(uploaded_file_obj.name)
        uploaded_file_name = '{}{}'.format(slugify(uploaded_file_name), uploaded_file_ext)
        uploaded_file_upload_path = '{}/{}'.format(self.request.user.username, uploaded_file_name)

        file_obj, created = File.objects.get_or_create(
            path=uploaded_file_upload_path,
            defaults={
                'volume': Volume.UPLOAD,
                'size': uploaded_file_obj.size
            }
        )

        if not created:
            return Response({
                'detail': "File already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Link file to authenticated user.
        request.user.files.add(file_obj)

        # Handle uploaded file.
        handle_uploaded_file(uploaded_file_obj, file_obj.full_path)

        return Response(status=status.HTTP_201_CREATED)
