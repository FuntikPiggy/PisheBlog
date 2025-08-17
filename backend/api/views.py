from functools import wraps

from django.contrib.admin.templatetags.admin_list import pagination
from django.contrib.auth import get_user_model
from django.db.models import Value, F
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from rest_framework import status, permissions, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.models import Tag, Ingredient, Recipe
from .filters import RecipeFilter
from .pagination import QueryPageNumberPagination, paginated
from .permissions import IsAuthorOrStaffOrReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeInSerializer, SubscriptionsSerializer,
                          RecipeOutSerializer, CustomUserSerializer)

User = get_user_model()


def manytomany_setter_deleter(func):
    """Декоратор для методов подписки,
    добавления в избранное и в корзину покупок."""
    @wraps(func)
    def wrapper(self, request, **kwargs):
        queryset = func(self, request, **kwargs)
        if request.method == 'POST':
            if queryset.filter(id=kwargs['id']).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            queryset.add(kwargs['id'])
            return Response(status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            queryset.remove(kwargs['id'])
            return Response(status=status.HTTP_204_NO_CONTENT)
    return wrapper


class FgUserViewSet(UserViewSet):
    """Представление модели пользователя."""

    http_method_names = ('get', 'post', 'put', 'delete',)
    permission_classes = (IsAuthorOrStaffOrReadOnly,)
    serializer_class = CustomUserSerializer
    pagination_class = QueryPageNumberPagination

    @paginated
    @action(('get',), detail=False, permission_classes=(permissions.AllowAny,),)
    def subscriptions(self, request):
        """Метод просмотра подписок."""
        return SubscriptionsSerializer(
            request.user.subscriptions.all(),
            many=True,
            context={'request': request},
        ).data

    @action(('put', 'delete'), url_path='me/avatar', detail=False, permission_classes=(permissions.AllowAny,),)
    def avatar(self, request, *args, **kwargs):
        """Метод добавления и удаления аватара."""
        self.get_object = self.get_instance
        if request.method == 'PUT':
            return self.partial_update(request, *args, **kwargs)
        elif request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @manytomany_setter_deleter
    @action(('post', 'delete',), detail=True, permission_classes=(permissions.AllowAny,),)
    def subscribe(self, request, *args, **kwargs):
        """Метод подписки."""
        return request.user.subscriptions


class TagViewSet(ReadOnlyModelViewSet):
    """Представление модели тэга."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None

    # def get_queryset(self):
    #     return Tag.objects.filter(recipes__isnull=False).distinct()


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление модели ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Представление модели рецепта."""

    http_method_names = ('get', 'post', 'patch', 'delete',)
    permission_classes = (permissions.AllowAny,)
    # queryset = Recipe.objects.prefetch_related(Prefetch('ingredients_amount', queryset=RecipeIngredient.objects.all()))
    queryset = Recipe.objects.all()#.prefetch_related('ingredients', 'recipeingredients')
    serializer_class = RecipeInSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_url_kwarg = 'id'

    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     if self.action in ('create', 'partial_update'):
    #         return context
    #     context.update({'queryset': self.queryset})
    #     return context

    # def get_queryset(self):
    #     # queryset = list(RecipeIngredient.objects.all().select_related('recipe', 'ingredient'))
    #     queryset = list(Recipe.objects.prefetch_related(Prefetch('ingredients_amount', queryset=RecipeIngredient.objects.all())))
    #     return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return self.serializer_class
        return RecipeOutSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @manytomany_setter_deleter
    @action(('post', 'delete',), detail=True, permission_classes=(permissions.AllowAny,),)
    def favorite(self, request, *args, **kwargs):
        """Метод добавления в избранное."""
        return request.user.favorites

    @manytomany_setter_deleter
    @action(('post', 'delete',), detail=True, permission_classes=(permissions.AllowAny,),)
    def shopping_cart(self, request, *args, **kwargs):
        """Метод добавления в корзину покупок."""
        return request.user.shopping_cart

    @action(('get',), detail=False, permission_classes=(permissions.AllowAny,),)
    def download_shopping_cart(self, request, *args, **kwargs):
        """Метод вывода списка покупок в файл."""
        ingredients = dict()
        all_ingrediens = list(
            request.user.shopping_cart.prefetch_related(
                'ingredients', 'recipeingredients'
            ).values('ingredients__name', 'recipeingredients__amount').values(
                name=F('ingredients__name'), amount=F('recipeingredients__amount')
            )
        )
        for ingredient in all_ingrediens:
            ingredients.setdefault(ingredient['name'], []).append(ingredient['amount'])
        return request.user.shopping_cart


    # @action()
    # def get_link(self, request):


    # def get_serializer_context(self):
    #     return {
    #         'request': self.request,
    #         'format': self.format_kwarg,
    #         'view': self,
    #         'tags': Tag.objects.all(),
    #     }
