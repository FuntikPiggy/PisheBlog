from functools import wraps

from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
import short_url

from recipes.models import Tag, Ingredient, Recipe
from .filters import RecipeFilter, IngredientFilter
from .pagination import QueryPageNumberPagination, paginated
from .permissions import IsAuthorOrStaff, SelfOrStaffOrReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeInSerializer, SubscriptionsSerializer,
                          RecipeOutSerializer, CustomUserSerializer)
from .shopping import save_shopping_file

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
    serializer_class = CustomUserSerializer
    pagination_class = QueryPageNumberPagination
    permission_classes = (IsAuthenticated, SelfOrStaffOrReadOnly,)

    @paginated
    @action(('get',), detail=False, permission_classes=(IsAuthenticated,),)
    def subscriptions(self, request):
        """Метод просмотра подписок."""
        return SubscriptionsSerializer(
            request.user.subscriptions.all(),
            many=True,
            context={'request': request},
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
    @action(('post', 'delete',), detail=True, permission_classes=(IsAuthenticated,),)
    def subscribe(self, request, *args, **kwargs):
        """Метод подписки."""
        return request.user.subscriptions


class TagViewSet(ReadOnlyModelViewSet):
    """Представление модели тэга."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None

    # def get_queryset(self):
    #     return Tag.objects.filter(recipes__isnull=False).distinct()


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление модели ингредиента."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    # filterset_fields = ('name',)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Представление модели рецепта."""

    http_method_names = ('get', 'post', 'patch', 'delete',)
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrStaff,)
    queryset = Recipe.objects.all().prefetch_related(
        'ingredients', 'recipeingredients', 'tags', 'author')
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

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ('create', 'partial_update'):
            return self.serializer_class
        return RecipeOutSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @manytomany_setter_deleter
    @action(('post', 'delete',), detail=True, permission_classes=(IsAuthenticated,),)
    def favorite(self, request, *args, **kwargs):
        """Метод добавления в избранное."""
        return request.user.favorites

    @manytomany_setter_deleter
    @action(('post', 'delete',), detail=True, permission_classes=(IsAuthenticated,),)
    def shopping_cart(self, request, *args, **kwargs):
        """Метод добавления в корзину покупок."""
        return request.user.shopping_cart

    @action(('get',), detail=False, permission_classes=(IsAuthenticated,),)
    def download_shopping_cart(self, request, *args, **kwargs):
        """Метод вывода списка покупок в файл."""
        ingredients = dict()
        all_ingrediens = list(
            request.user.shopping_cart.prefetch_related(
                'ingredients', 'recipeingredients').values(
                'ingredients__name',
                'recipeingredients__amount',
                'ingredients__measurement_unit'
            ).values(
                name=F('ingredients__name'),
                amount=F('recipeingredients__amount'),
                m_unit=F('ingredients__measurement_unit'),
            )
        )
        for ingredient in all_ingrediens:
            ingredients.setdefault(
                (ingredient['name'], ingredient['m_unit']), []
            ).append(ingredient['amount'])
        ingredients = [
            (k[0], f'{sum(v)} {k[1]}') for k, v in sorted(ingredients.items())
        ]
        return save_shopping_file(sorted(ingredients))

    @action(('get',), url_path='get-link', detail=True, permission_classes=(AllowAny,),)
    def get_link(self, request, *args, **kwargs):
        """Метод получения короткой ссылки."""
        return Response(
            {'short-link':f'http://{request.get_host()}/s/{short_url.encode_url(int(kwargs['id']), min_length=3)}'},
            status=status.HTTP_200_OK
        )


def short_link_decode(request, shorturl):
    """Функция представления для декодирования коротких ссылок."""
    a = short_url.decode_url(shorturl)
    return redirect(
        f'http://{request.get_host()}/{reverse('api:recipe-detail', kwargs={'id':short_url.decode_url(shorturl),},)}'
        )
