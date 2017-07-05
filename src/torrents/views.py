from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Torrent
from .serializers import TorrentSerializer
from .utils import transmission


class TorrentViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Torrent.objects.all()
    serializer_class = TorrentSerializer

    def get_queryset(self):
        return self.request.user.torrents.all()

    def create(self, request, *args, **kwargs):
        link = request.data.get('link', '').strip()
        url_validator = URLValidator()

        try:
            if not link.startswith('magnet:'):
                url_validator(link)
                if not link.endswith('.torrent'):
                    raise ValidationError("Invalid torrent URL.")
        except ValidationError as e:
            return Response({'detail': e}, status=status.HTTP_400_BAD_REQUEST)

        torrent = transmission.add_torrent(link)
        torrent_model, created = Torrent.objects.get_or_create(
            hash=torrent.hashString,
            defaults={
                'name': torrent.name,
                'private': torrent.isPrivate,
            },
        )

        request.user.torrents.add(torrent_model)

        return Response(
            self.serializer_class(torrent_model).data,
            status=created and status.HTTP_201_CREATED or status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        torrent_model = self.get_object()
        self.request.user.torrents.remove(torrent_model)

        return Response(status=status.HTTP_204_NO_CONTENT)
