import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
# from django.core.paginator import Paginator
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient, Followings, Favorite, Purchase

User = get_user_model()


# class IsSubscribedMixin(UserSerializer):
#     """Миксин подписок пользователя."""
#
#     is_subscribed = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = ['email', 'id', 'username', 'first_name',
#                   'last_name', 'is_subscribed', 'avatar']
#
#     def get_is_subscribed(self, user):
#         if self.context['request'].user.is_authenticated:
#             return self.context['request'].user.subscriptions.filter(id=user.id).exists()
#         return False


class CustomUserSerializer(UserSerializer):
    """Сериализатор данных модели FoodgramUser."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = (*UserSerializer.Meta.fields, 'is_subscribed', 'avatar',)
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, user):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user.subscriptions.filter(following_id=user.id).exists()
        return False


class AvatarUserSerializer(UserSerializer):

    avatar = Base64ImageField(required=True,)

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('avatar',)


class BriefRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Recipe для Subscriptions."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class FollowingsSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Followings."""

    class Meta:
        model = Followings
        fields = ('id', 'user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Followings.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate(self, Following):
        if Following['user'] == Following['following']:
            raise serializers.ValidationError()
        return Following


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Favorite."""

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class PurchaseSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Purchase."""

    class Meta:
        model = Purchase
        fields = ('id', 'user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Purchase.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class UserSubscriptionsSerializer(UserSerializer):
    """Сериализатор данных модели пользователя для модели Subscriptions."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)
    recipes = serializers.SerializerMethodField()#RecipeSerializer()#serializers.SerializerMethodField('paginated_recipes')
    recipes_count = serializers.IntegerField(source='recipes.count')#serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (*UserSerializer.Meta.fields, 'recipes',
                  'recipes_count', 'is_subscribed', 'avatar',)
        read_only_fields = ('recipes', 'recipes_count', 'is_subscribed',)

    def get_recipes(self, user):
        recipes = user.recipes.all()
        limit = self.context.get('request').query_params.get(
            'recipes_limit', None)
        if limit is not None:
            recipes = recipes[:int(limit)]
        return BriefRecipeSerializer(recipes, many=True).data
    #     return RecipeSerializer(Paginator(
    #         user.recipes.all(),
    #         self.context['request'].query_params.get('recipes_limit', 3)
    #     ).page(1), many=True, ).data

    # def get_recipes_count(self, user):
    #     a = True
    #     return user.recipes.count()

    def get_is_subscribed(self, user):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user.subscriptions.filter(following_id=user.id).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = ('name', 'measurement_unit',)


# class IngredientAmountSerializer(serializers.ModelSerializer):
#     """Сериализатор данных модели Ingredient для
#      сериализатора вывода модели Recipe."""
#
#     # amount = serializers.IntegerField(validators=())
#
#     class Meta:
#         model = Ingredient
#         fields = ('id', 'name', 'measurement_unit', 'amount',)
#         read_only_fields = ('name', 'measurement_unit', 'amount',)


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый класс для сериализаторов модели Recipe."""

    author = CustomUserSerializer(read_only=True,)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time',)
        read_only_fields = ('id', 'author', 'tags', 'ingredients',
                            'is_favorited', 'is_in_shopping_cart',)

    def get_ingredients(self, recipe):
        recipe_ingredients = {
            d.ingredient_id: d.amount for d in recipe.recipeingredients.all()}
        ingredients = recipe.ingredients.all()
        serializer = IngredientSerializer(ingredients, many=True)
        for ingredient in serializer.data:
            ingredient['amount'] = recipe_ingredients[ingredient['id']]
        return serializer.data

    def get_is_favorited(self, recipe):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user.favorites.filter(
                recipe_id=recipe.id).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user.purchases.filter(
                recipe_id=recipe.id).exists()
        return False


class RecipeInSerializer(serializers.ModelSerializer):
    """Сериализатор ввода данных модели Recipe."""

    tags = PresentablePrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        presentation_serializer=TagSerializer,
        many=True,
        required=True
    )
    ingredients = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True,)
    image = Base64ImageField(required=True, allow_null=False, )
    is_favorited = serializers.SerializerMethodField(read_only=True,)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True,)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = ('id',)
        required_fields = ('cooking_time',)

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError()
        return image

    # def validate_tags(self, tags):
    #     if not tags or len(tags) == 0 or len(tags) != len(set(tags)):
    #         raise serializers.ValidationError()
    #     return tags

    @staticmethod
    def create_update(recipe, tags, ingredients_amounts):
        recipe.tags.set(tags)
        recipe.ingredients.clear()
        recipeingredients = [RecipeIngredient(
            recipe=recipe,
            ingredient=Ingredient.objects.get(id=i[0]),
            amount=i[1]
        ) for i in ingredients_amounts]
        RecipeIngredient.objects.bulk_create(recipeingredients)
        return recipe

    def get_check_ingredients_and_tags(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients_amounts = [
            (i['id'], int(i['amount']))
            for i in self.initial_data.pop('ingredients', [])
        ]
        if (not ingredients_amounts #or not tags
                or len(ingredients_amounts) != len(set(ingredients_amounts))
                or len(tags) != len(set(tags)) or len(tags) == 0
                or not all(Ingredient.objects.filter(id=i[0]).exists()
                           and i[1]>0
                           for i in ingredients_amounts)):
            raise serializers.ValidationError()
        return tags, ingredients_amounts

    def create(self, validated_data):
        tags, ingredients_amounts = self.get_check_ingredients_and_tags(
            validated_data)
        recipe = super().create(validated_data)
        return self.create_update(recipe, tags, ingredients_amounts)

    def update(self, recipe, validated_data):
        tags, ingredients_amounts = self.get_check_ingredients_and_tags(
            validated_data)
        super().update(recipe, validated_data)
        return self.create_update(recipe, tags, ingredients_amounts)

    def get_ingredients(self, recipe):
        recipe_ingredients = {
            d.ingredient_id: d.amount for d in recipe.recipeingredients.all()}
        ingredients = recipe.ingredients.all()
        serializer = IngredientSerializer(ingredients, many=True)
        for ingredient in serializer.data:
            ingredient['amount'] = recipe_ingredients[ingredient['id']]
        return serializer.data

    def get_is_favorited(self, recipe):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user.favorites.filter(
                recipe_id=recipe.id).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user.purchases.filter(
                recipe_id=recipe.id).exists()
        return False
