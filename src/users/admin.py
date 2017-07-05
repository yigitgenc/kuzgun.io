from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rest_framework.authtoken.models import Token


class TokenInline(admin.StackedInline):
    model = Token
    show_change_link = True


class UserAdmin(BaseUserAdmin):
    inlines = (TokenInline, )

admin.site.register(get_user_model(), UserAdmin)
