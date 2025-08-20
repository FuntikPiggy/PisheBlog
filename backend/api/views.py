from functools import wraps

from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, filters
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, AllowAny)
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from short_url import encode_url, decode_url

from recipes.models import Tag, Ingredient, Recipe
from .filters import RecipeFilter, IngredientFilter
from .pagination import QueryPageNumberPagination, paginated
from .permissions import IsAuthorOrStaff, SelfOrStaffOrReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeInSerializer, SubscriptionsSerializer,
                          RecipeOutSerializer, CustomUserSerializer,
                          SubscriptionRecipeSerializer)
from .shopping import save_shopping_file

User = get_user_model()


def manytomany_setter_deleter(func):
    """Декоратор для методов подписки,
    добавления в избранное и в корзину покупок."""
    @wraps(func)
    def wrapper(self, request, **kwargs):
        queryset, serializer_class = func(self, request, **kwargs)
        if request.method == 'POST':
            if queryset.filter(id=kwargs['id']).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            queryset.add(kwargs['id'])
            return Response(
                serializer_class(queryset.get(id=kwargs['id']),
                                 context={'request': request},).data,
                status=status.HTTP_201_CREATED,
            )
        elif request.method == 'DELETE':
            queryset.remove(kwargs['id'])
            return Response(status=status.HTTP_204_NO_CONTENT)
    return wrapper


class FgUserViewSet(UserViewSet):
    """Представление модели пользователя."""

    http_method_names = ('get', 'post', 'put', 'delete',)
    serializer_class = CustomUserSerializer
    pagination_class = QueryPageNumberPagination
    permission_classes = (IsAuthenticated, SelfOrStaffOrReadOnly,)

    @paginated
    @action(('get',), detail=False, permission_classes=(IsAuthenticated,),)
    def subscriptions(self, request):
        """Метод просмотра подписок."""
        return SubscriptionsSerializer(request.user.subscriptions.all(),
                                       many=True, context={'request': request},
                                       ).data

    @action(
        ('put', 'delete'), url_path='me/avatar',
        detail=False, permission_classes=(IsAuthorOrStaff,),
    )
    def avatar(self, request, *args, **kwargs):
        """Метод добавления и удаления аватара."""
        self.get_object = self.get_instance
        if request.method == 'PUT':
            return self.partial_update(request, *args, **kwargs)
        elif request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @manytomany_setter_deleter
    @action(('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,),)
    def subscribe(self, request, *args, **kwargs):
        """Метод подписки."""
        return request.user.subscriptions, SubscriptionsSerializer


class TagViewSet(ReadOnlyModelViewSet):
    """Представление модели тэга."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление модели ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Представление модели рецепта."""

    http_method_names = ('get', 'post', 'patch', 'delete',)
    permission_classes = (IsAuthenticatedOrReadOnly | SelfOrStaffOrReadOnly,)
    queryset = Recipe.objects.all().prefetch_related(
        'ingredients', 'recipeingredients', 'tags', 'author')
    serializer_class = RecipeOutSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_url_kwarg = 'id'

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ('create', 'partial_update'):
            return RecipeInSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(
            author=self.request.user,
            tags=self.request.data.get('tags', []),
            ingredients=self.request.data.get('ingredients', []),
        )

    @manytomany_setter_deleter
    @action(('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,),)
    def favorite(self, request, *args, **kwargs):
        """Метод добавления в избранное."""
        return request.user.favorites, SubscriptionRecipeSerializer

    @manytomany_setter_deleter
    @action(('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,),)
    def shopping_cart(self, request, *args, **kwargs):
        """Метод добавления в корзину покупок."""
        return request.user.shopping_cart, SubscriptionRecipeSerializer

    @action(('get',), detail=False,
            permission_classes=(IsAuthenticated,),)
    def download_shopping_cart(self, request, *args, **kwargs):
        """Метод вывода списка покупок в файл."""
        all_ingredients = request.user.shopping_cart.prefetch_related(
            'ingredients', 'recipeingredients').values(
            ing_name=F('ingredients__name'),
            ing_amount=F('recipeingredients__amount'),
            ing_m_unit=F('ingredients__measurement_unit')
        )
        ingredients = dict()
        for ingredient in all_ingredients:
            ingredients.setdefault(
                (ingredient['ing_name'], ingredient['ing_m_unit']), []
            ).append(ingredient['ing_amount'])
        ingredients = [
            (k[0], f'{sum(v)} {k[1]}') for k, v in ingredients.items()
        ]
        return save_shopping_file(ingredients)

    @action(('get',), url_path='get-link',
            detail=True, permission_classes=(AllowAny,),)
    def get_link(self, request, *args, **kwargs):
        """Метод получения короткой ссылки."""
        return Response(
            {'short-link': f'https://{request.get_host()}'
                           f'/s/{encode_url(int(kwargs['id']))}'},
            status=status.HTTP_200_OK,
        )


@permission_classes((IsAuthenticatedOrReadOnly,))
def short_link_decode(request, shorturl):
    """Функция представления для декодирования коротких ссылок."""
    return redirect(
        request.build_absolute_uri().replace(
            request.get_full_path(),
            f'/recipes/{decode_url(shorturl)}'
        )
    )
