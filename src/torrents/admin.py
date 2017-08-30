from django.contrib import admin

from .models import Torrent


class TorrentAdmin(admin.ModelAdmin):
    """
    Django admin page for Torrent model.
    """
    model = Torrent
    list_display = ('name', 'hash')
    readonly_fields = ('hash', )


admin.site.register(Torrent, TorrentAdmin)
