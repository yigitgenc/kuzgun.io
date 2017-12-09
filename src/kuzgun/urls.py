"""
kuzgun.io URL configuration.
"""

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.documentation import include_docs_urls

from .views import HomeView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/docs/', include_docs_urls(title='Kuzgun.io API', description='Dockerized online streaming software.')),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/auth/token', obtain_auth_token),
    url(r'^api/users/', include('users.urls', namespace='users')),
    url(r'^api/torrents/', include('torrents.urls', namespace='torrents')),
    url(r'^api/files/', include('files.urls', namespace='files')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
