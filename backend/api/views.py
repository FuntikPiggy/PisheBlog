from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly, AllowAny)
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.models import (Tag, Ingredient, Recipe,
                            Favorite, Purchase, Subscription, )
from .filters import RecipeFilter, IngredientFilter
from .permissions import AuthorOrReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          UserSubscriptionsSerializer,
                          FoodgramUserSerializer,
                          BriefRecipeSerializer, RecipeSerializer,
                          AvatarUserSerializer, )
from .shopping import save_shopping_file

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    """Представление модели пользователя."""

    http_method_names = ('get', 'post', 'put', 'delete',)
    serializer_class = FoodgramUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AuthorOrReadOnly,)

    @action(('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,),)
    def subscribe(self, request, *args, **kwargs):
        """Метод подписки."""
        if request.method == 'DELETE':
            get_object_or_404(
                Subscription, user=request.user, author=kwargs['id']
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        author = get_object_or_404(User, id=kwargs['id'])
        if Subscription.objects.filter(
                user=request.user, author=author
        ).exists():
            raise ValidationError(f'Вы уже подписаны на пользователя '
                                  f'{author.last_name} {author.first_name}')
        if request.user == author:
            raise ValidationError('Нельзя подписаться на себя!')
        Subscription.objects.create(user=request.user, author=author)
        return Response(
            UserSubscriptionsSerializer(
                author, context={'request': request},).data,
            status=status.HTTP_201_CREATED,
        )

    @action(('get',), detail=False, permission_classes=(IsAuthenticated,),)
    def subscriptions(self, request):
        """Метод просмотра подписок."""
        page = self.paginate_queryset(
            UserSubscriptionsSerializer(
                User.objects.filter(
                    id__in=request.user.subscriptions_added.values('author'),),
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
        return super().me(request, *args, **kwargs)

    @action(
        ('put', 'delete'), url_path='me/avatar',
        detail=False, permission_classes=(IsAuthenticated, AuthorOrReadOnly,),
    )
    def avatar(self, request, *args, **kwargs):
        """Метод добавления и удаления аватара."""
        if request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = AvatarUserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ReadOnlyModelViewSet):
    """Представление модели тэга."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление модели продукта."""

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
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_url_kwarg = 'id'

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def favorite_shopping_base(request, klass, queryset, id):
        """Базовый метод для методов добавления в избранное и корзину>."""
        if request.method == 'DELETE':
            get_object_or_404(klass, user=request.user, recipe=id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        recipe = get_object_or_404(Recipe, id=id)
        if klass.objects.filter(user=request.user, recipe=recipe).exists():
            raise ValidationError(f'{recipe.name} уже есть в '
                                  f'{klass._meta.verbose_name_plural}!')
        klass.objects.create(user=request.user, recipe=recipe)
        return Response(
            BriefRecipeSerializer(
                recipe, context={'request': request},).data,
            status=status.HTTP_201_CREATED,
        )

    @action(('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,),)
    def favorite(self, request, id):
        """Метод добавления в избранное."""
        return self.favorite_shopping_base(
            request, Favorite, request.user.favorites, id)

    @action(('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,),)
    def shopping_cart(self, request, id):
        """Метод добавления в корзину покупок."""
        return self.favorite_shopping_base(
            request, Purchase, request.user.purchases, id)

    @action(('get',), detail=False,
            permission_classes=(IsAuthenticated,),)
    def download_shopping_cart(self, request, *args, **kwargs):
        """Метод вывода списка покупок в файл."""
        ingredients = request.user.purchases.prefetch_related(
            'recipe', 'recipe__ingredients', 'recipe__recipeingredients',
        ).values(
            name=F('recipe__ingredients__name'),
            m_unit=F('recipe__ingredients__measurement_unit'),
        ).annotate(
            amount=Sum('recipe__recipeingredients__amount'),
        ).order_by('recipe__ingredients__name')
        recipes = request.user.purchases.prefetch_related(
            'recipe', 'recipe__author'
        )
        return save_shopping_file(ingredients, recipes)

    @action(('get',), url_path='get-link',
            detail=True, permission_classes=(AllowAny,),)
    def get_link(self, request, id):
        """Метод получения короткой ссылки."""
        if not Recipe.objects.filter(id=id).exists():
            raise Http404(f'Рецепта с id {id} в базе нет')
        return Response(
            {'short-link': request.build_absolute_uri(
                reverse('recipes:short-link', args=(id,)),
            ), },
            status=status.HTTP_200_OK,
        )
