from django.contrib.auth import get_user_model
from rest_framework.decorators import list_route
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import UserSerializer


class UserViewSet(UpdateModelMixin, GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.queryset.filter(pk=self.request.user.pk)

    @list_route(methods=['GET'])
    def me(self, request):
        user = get_object_or_404(self.queryset, pk=request.user.pk)
        serializer = self.get_serializer(user)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        kwargs.update({'partial': True})
        return super(UserViewSet, self).update(request, *args, **kwargs)
