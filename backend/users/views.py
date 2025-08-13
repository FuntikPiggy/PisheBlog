from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import SubscriptionsSerializer


User = get_user_model()


class FgUserViewSet(UserViewSet):
    http_method_names = ['get', 'post', 'put', 'delete']

    @action(['get',], url_path='subscriptions', detail=False)
    def get_subscriptions(self, request):
        return Response(
            SubscriptionsSerializer(
                request.user.subscriptions.all(),
                many=True,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(['put', 'delete'], url_path='me/avatar', detail=False)
    def avatar(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == 'PUT':
            return self.partial_update(request, *args, **kwargs)
        elif request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
