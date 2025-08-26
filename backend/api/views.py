# from functools import wraps

from django.contrib.auth import get_user_model
from django.db.models import F, Sum, Value
from django.db.models.functions import Concat
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, filters
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, AllowAny)
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from short_url import encode_url, decode_url

from recipes.models import Tag, Ingredient, Recipe, Favorite, Purchase, Followings
from .filters import RecipeFilter, IngredientFilter
from .permissions import AuthorOrReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeInSerializer, UserSubscriptionsSerializer,
                          CustomUserSerializer,
                          BriefRecipeSerializer, BaseRecipeSerializer, AvatarUserSerializer, FollowingsSerializer,
                          FavoriteSerializer, PurchaseSerializer)
from .shopping import save_shopping_file

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    """Представление модели пользователя."""

    http_method_names = ('get', 'post', 'put', 'delete',)
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorOrReadOnly,)

    @action(('get',), detail=False, permission_classes=(IsAuthenticated,),)
    def subscriptions(self, request):
        """Метод просмотра подписок."""
        page = self.paginate_queryset(
            UserSubscriptionsSerializer(
                User.objects.filter(id__in=request.user.subscriptions.values('following'),),
                many=True,
                context={'request': request},
            ).data
        )
        return self.get_paginated_response(page)

    @action(
        ('get',),
        detail=False, permission_classes=(IsAuthenticated,),
    )
    def me(self, request, *args, **kwargs):
        """Метод добавления и удаления аватара."""
        return Response(
            self.get_serializer(request.user).data,
            status=status.HTTP_200_OK
        )

    @action(
        ('put', 'delete'), url_path='me/avatar',
        detail=False, permission_classes=(IsAuthenticated, AuthorOrReadOnly,),
    )
    def avatar(self, request, *args, **kwargs):
        """Метод добавления и удаления аватара."""
        # self.get_object = self.get_instance
        if request.method == 'PUT':
            serializer = AvatarUserSerializer(request.user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,),)
    def subscribe(self, request, *args, **kwargs):
        """Метод подписки."""
        following = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'POST':
            serializer = FollowingsSerializer(
                data={'user': request.user.id, 'following': following.id})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            # Followings.objects.create(user=request.user, following=following)
            return Response(
                UserSubscriptionsSerializer(
                    following, context={'request': request},).data,
                status=status.HTTP_201_CREATED,
            )
        elif request.method == 'DELETE':
            # a = Followings.objects.get(user=request.user, following=following)
            # get_object_or_404(Followings, user=request.user, following=following)
            # if serializer.is_valid(raise_exception=True):
            #     serializer.delete()
            subscribe = Followings.objects.filter(user=request.user, following=following)
            if not subscribe.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorOrReadOnly,)
    queryset = Recipe.objects.all().prefetch_related(
        'ingredients', 'recipeingredients', 'tags', 'author')
    serializer_class = BaseRecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_url_kwarg = 'id'


    def get_serializer_class(self, *args, **kwargs):
        if self.action in ('create', 'partial_update'):
            return RecipeInSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def favorite_shopping_base(request, klass, serializer, **kwargs):
        """Базовый метод для методов добавления в избранное и корзину>."""
        recipe = get_object_or_404(Recipe, id=kwargs['id'])
        if request.method == 'POST':
            serializer = serializer(
                data={'user': request.user.id, 'recipe': recipe.id})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            # klass.objects.create(user=request.user, recipe=recipe)
            return Response(
                BriefRecipeSerializer(
                    recipe, context={'request': request},).data,
                status=status.HTTP_201_CREATED,
            )
        elif request.method == 'DELETE':
            klass_obj = klass.objects.filter(user=request.user, recipe=recipe)
            if not klass_obj.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            klass_obj.delete()
            # get_object_or_404(klass, user=request.user, recipe=recipe)
            # klass.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


    @action(('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,),)
    def favorite(self, request, **kwargs):
        """Метод добавления в избранное."""
        return self.favorite_shopping_base(
            request, Favorite,  FavoriteSerializer, **kwargs)

    @action(('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,),)
    def shopping_cart(self, request, *args, **kwargs):
        """Метод добавления в корзину покупок."""
        return self.favorite_shopping_base(
            request, Purchase, PurchaseSerializer, **kwargs)

    @action(('get',), detail=False,
            permission_classes=(IsAuthenticated,),)
    def download_shopping_cart(self, request, *args, **kwargs):
        """Метод вывода списка покупок в файл."""
        ingredients = request.user.purchases.prefetch_related(
            'recipe', 'recipe__ingredients', 'recipe__recipeingredients',
        ).values(
            name=F('recipe__ingredients__name'),
            m_unit=F('recipe__ingredients__measurement_unit'),
        ).annotate(amount=Sum('recipe__recipeingredients__amount'),)
        recipes = request.user.purchases.prefetch_related(
            'recipe', 'recipe__author'
        ).values(
            name=F('recipe__name'),
            author=Concat(
                'recipe__author__first_name',
                Value(' '),
                'recipe__author__last_name',
            ),)
        return save_shopping_file(ingredients, recipes)

    @action(('get',), url_path='get-link',
            detail=True, permission_classes=(AllowAny,),)
    def get_link(self, request, id):
        """Метод получения короткой ссылки."""
        get_object_or_404(Recipe, id=id)
        return Response(
            {'short-link': request.build_absolute_uri(
                reverse('recipes:short-link', args=(id,)),
            ), },
            status=status.HTTP_200_OK,
        )
