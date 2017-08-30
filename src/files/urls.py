"""
URL configuration for File API endpoint.
"""

from rest_framework.routers import DefaultRouter

from .views import FileViewSet


router = DefaultRouter()
router.register(r'', FileViewSet)

urlpatterns = router.urls
