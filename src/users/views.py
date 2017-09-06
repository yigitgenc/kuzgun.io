from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import UserSerializer


class UserViewSet(UpdateModelMixin, GenericViewSet):
    """
    User API endpoint for User model. (/users).
    Supported methods: Update
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    @list_route(methods=['GET'])
    def me(self, request):
        """
        Retrieves information of the user.

        :return: Response
        """
        user = get_object_or_404(self.queryset, pk=request.user.pk)
        serializer = self.get_serializer(user)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        Partial update the user.

        :return: super
        """
        kwargs.update({'partial': True})
        super(UserViewSet, self).update(request, *args, **kwargs)

        return Response(status=status.HTTP_204_NO_CONTENT)
