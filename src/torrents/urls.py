from rest_framework_extensions.routers import ExtendedDefaultRouter

from files.views import FileViewSet
from .views import TorrentViewSet


router = ExtendedDefaultRouter()
router.register(r'', TorrentViewSet).register(
    r'files',
    FileViewSet,
    base_name='torrent-files',
    parents_query_lookups=['torrent']
)

urlpatterns = router.urls
