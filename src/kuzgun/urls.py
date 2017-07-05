from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/auth/token', obtain_auth_token),
    url(r'^api/users/', include('users.urls', namespace='users')),
    url(r'^api/torrents/', include('torrents.urls', namespace='torrents')),
    url(r'^api/files/', include('files.urls'), name='files'),
]
