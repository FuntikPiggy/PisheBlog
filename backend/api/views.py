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
                          BriefRecipeSerializer, BaseRecipeSerializer)
from .shopping import save_shopping_file

User = get_user_model()


# def manytomany_setter_deleter(func):
#     """Декоратор для методов подписки,
#     добавления в избранное и в корзину покупок."""
#     @wraps(func)
#     def wrapper(self, request, **kwargs):
#         queryset, serializer_class = func(self, request, **kwargs)
#         if request.method == 'POST':
#             if queryset.filter(id=kwargs['id']).exists():
#                 return Response(status=status.HTTP_400_BAD_REQUEST)
#             queryset.add(kwargs['id'])
#             return Response(
#                 serializer_class(queryset.get(id=kwargs['id']),
#                                  context={'request': request},).data,
#                 status=status.HTTP_201_CREATED,
#             )
#         elif request.method == 'DELETE':
#             queryset.remove(kwargs['id'])
#             return Response(status=status.HTTP_204_NO_CONTENT)
#     return wrapper


class FoodgramUserViewSet(UserViewSet):
    """Представление модели пользователя."""

    http_method_names = ('get', 'post', 'put', 'delete',)
    serializer_class = CustomUserSerializer
    # pagination_class = QueryPageNumberPagination
    permission_classes = (AllowAny,)# IsAuthenticated, SelfOrStaffOrReadOnly,)


    # def get_serializer_context(self):
    #     return {
    #         'request': self.request,
    #         ''
    #     }

    # @paginated
    @action(('get',), detail=False, permission_classes=(AllowAny,),)#(IsAuthenticated,),)
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
        detail=False, permission_classes=(AllowAny,),#IsAuthorOrStaff,),
    )
    def avatar(self, request, *args, **kwargs):
        """Метод добавления и удаления аватара."""
        self.get_object = self.get_instance
        if request.method == 'PUT':
            return self.partial_update(request, *args, **kwargs)
        elif request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    # @manytomany_setter_deleter
    @action(('post', 'delete',), detail=True,
            permission_classes=(AllowAny,),)#IsAuthenticated,),)
    def subscribe(self, request, *args, **kwargs):
        """Метод подписки."""
        following = User.objects.get(id=kwargs['id'])
        if request.method == 'POST':
            Followings.objects.create(user=request.user, following=following)
            return Response(
                UserSubscriptionsSerializer(
                    following, context={'request': request},).data,
                status=status.HTTP_201_CREATED,
            )
        elif request.method == 'DELETE':
            Favorite.objects.get(
                user=request.user, following=following).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # return request.user.subscriptions, UserSubscriptionsSerializer


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
    permission_classes = (IsAuthenticatedOrReadOnly | AuthorOrReadOnly,)
    queryset = Recipe.objects.all().prefetch_related(
        'ingredients', 'recipeingredients', 'tags', 'author')
    serializer_class = BaseRecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_url_kwarg = 'id'
    # pagination_class = RecipesQueryPageLimitPagination

    # def get_queryset(self):
    #     if 'recipes_limit' in self.kwargs:
    #         return Recipe.objects.all()[:3]
    #     return Recipe.objects.all().prefetch_related(
    #     'ingredients', 'recipeingredients', 'tags', 'author')

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ('create', 'partial_update'):
            return RecipeInSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def perform_update(self, serializer):
    #     serializer.save(
    #         author=self.request.user,
    #         tags=self.request.data.get('tags', []),
    #         ingredients=self.request.data.get('ingredients', []),
    #     )

    @staticmethod
    def favorite_shopping_base(request, klass, **kwargs):
        """Базовый метод для методов добавления в избранное и корзину>."""
        recipe = Recipe.objects.get(id=kwargs['id'])
        if request.method == 'POST':
            klass.objects.create(user=request.user, recipe=recipe)
            return Response(
                BriefRecipeSerializer(
                    recipe, context={'request': request},).data,
                status=status.HTTP_201_CREATED,
            )
        elif request.method == 'DELETE':
            klass.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


    # @manytomany_setter_deleter
    @action(('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,),)
    def favorite(self, request, **kwargs):
        """Метод добавления в избранное."""
        return self.favorite_shopping_base(request, Favorite, **kwargs)
        # recipe = Recipe.objects.get(id=kwargs['id'])
        # if request.method == 'POST':
        #     Favorite.objects.create(user=request.user, recipe=recipe)
        #     return Response(
        #         BriefRecipeSerializer(
        #             recipe, context={'request': request},).data,
        #         status=status.HTTP_201_CREATED,
        #     )
        # elif request.method == 'DELETE':
        #     Favorite.objects.get(user=request.user, recipe=recipe).delete()
        #     return Response(status=status.HTTP_204_NO_CONTENT)

    # @manytomany_setter_deleter
    @action(('post', 'delete',), detail=True,
            permission_classes=(IsAuthenticated,),)
    def shopping_cart(self, request, *args, **kwargs):
        """Метод добавления в корзину покупок."""
        return self.favorite_shopping_base(request, Purchase, **kwargs)
        # recipe = Recipe.objects.get(id=kwargs['id'])
        # if request.method == 'POST':
        #     Purchase.objects.create(user=request.user, recipe=recipe)
        #     return Response(
        #         BriefRecipeSerializer(
        #             recipe, context={'request': request},).data,
        #         status=status.HTTP_201_CREATED,
        #     )
        # elif request.method == 'DELETE':
        #     Purchase.objects.get(user=request.user, recipe=recipe).delete()
        #     return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('get',), detail=False,
            permission_classes=(IsAuthenticated,),)
    def download_shopping_cart(self, request, *args, **kwargs):
        """Метод вывода списка покупок в файл."""
        # all_ingredients = request.user.shopping_cart.prefetch_related(
        #     'ingredients', 'recipeingredients').values(
        #     ing_name=F('ingredients__name'),
        #     ing_amount=F('recipeingredients__amount'),
        #     ing_m_unit=F('ingredients__measurement_unit')
        # )
        ingredients = request.user.purchases.prefetch_related(
            'recipe', 'recipe__ingredients', 'recipe__recipeingredients',).values(
            name=F('recipe__ingredients__name'),
            m_unit=F('recipe__ingredients__measurement_unit'),
        ).annotate(amount=Sum('recipe__recipeingredients__amount'),)
        recipes = request.user.purchases.prefetch_related('recipe', 'recipe__author').values(
            name=F('recipe__name'),
            author=Concat(
                'recipe__author__first_name',
                Value(' '),
                'recipe__author__last_name',
            ),)
        # all_ingredients = request.user.purchases.prefetch_related(
        #     'recipe',).values(
        #     ing_name=F('ingredients__name'),
        #     # ing_amount=F('recipeingredients__amount'),
        #     ing_m_unit=F('ingredients__measurement_unit')
        # ).annotate(ing_amount=Sum('recipe__ingredients__amount'),)
        # ingredients = dict()
        # for ingredient in all_ingredients:
        #     ingredients.setdefault(
        #         (ingredient['ing_name'], ingredient['ing_m_unit']), []
        #     ).append(ingredient['ing_amount'])
        # ingredients = [
        #     (k[0], f'{sum(v)} {k[1]}') for k, v in ingredients.items()
        # ]
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
