from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from rest_framework.authtoken.models import Token


class TokenInline(admin.StackedInline):
    """
    Django admin inline for Token model.
    """
    model = Token
    show_change_link = True


class UserAdmin(BaseUserAdmin):
    """
    Django admin page for User model.
    Inlines Token model.
    """
    inlines = (TokenInline, )


admin.site.register(get_user_model(), UserAdmin)
