from django.contrib import admin

from .models import File


class FileAdmin(admin.ModelAdmin):
    """
    Django admin page for File model.
    """
    model = File


admin.site.register(File, FileAdmin)

