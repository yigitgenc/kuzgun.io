from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer class of the User model.
    """
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'token')

    def get_token(self, obj):
        """
        Get the key from Token object.

        :param obj: User object
        :return: str
        """
        return Token.objects.get(user__pk=obj.pk).key
