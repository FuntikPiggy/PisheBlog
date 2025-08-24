import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
# from django.core.paginator import Paginator
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from drf_extra_fields.relations import PresentablePrimaryKeyRelatedField
from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient

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


# class Base64ImageField(serializers.ImageField):
#     """Класс поля для изображений."""
#
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             format, imgstr = data.split(';base64,')
#
#             ext = format.split('/')[-1]
#
#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
#
#         return super().to_internal_value(data)


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


class BriefRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Recipe для Subscriptions."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class UserSubscriptionsSerializer(UserSerializer):
    """Сериализатор данных модели Subscriptions."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)
    recipes = serializers.SerializerMethodField('paginated_recipes')#RecipeSerializer()#serializers.SerializerMethodField('paginated_recipes')
    recipes_count = serializers.IntegerField(source='recipes.count')#serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (*UserSerializer.Meta.fields, 'recipes',
                  'recipes_count', 'is_subscribed', 'avatar',)
        read_only_fields = ('recipes', 'recipes_count', 'is_subscribed',)

    def paginated_recipes(self, user):
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


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Ingredient для
     сериализатора вывода модели Recipe."""

    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый класс для сериализаторов модели Recipe."""

    author = CustomUserSerializer(read_only=True,)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

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
        for ingredient in ingredients:
            ingredient.amount = recipe_ingredients[ingredient.id]
        serializer = IngredientAmountSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, recipe):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user.favorites.filter(recipe_id=recipe.id).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user.purchases.filter(recipe_id=recipe.id).exists()
        return False


class RecipeInSerializer(serializers.ModelSerializer):
    """Сериализатор ввода данных модели Recipe."""

    tags = PresentablePrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        presentation_serializer=TagSerializer,
        many=True,
    )
    ingredients = serializers.SerializerMethodField(read_only=True)
    author = CustomUserSerializer(read_only=True,)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients_amounts = self.initial_data['ingredients']
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        recipeingredients = []
        for ingredient_amount in ingredients_amounts:
            ingredient = Ingredient.objects.get(id=ingredient_amount['id'])
            amount = ingredient_amount['amount']
            recipeingredients.append(RecipeIngredient(
                ingredient=ingredient, recipe=recipe, amount=amount,
            ))
        RecipeIngredient.objects.bulk_create(recipeingredients)
        return recipe

    def update(self, recipe, validated_data):
        new_tags = Tag.objects.filter(id__in=validated_data.pop('tags'))
        recipe.tags.set(new_tags)
        recipe.ingredients.clear()
        recipeingredients = [RecipeIngredient(
            recipe=recipe,
            ingredient=Ingredient.objects.get(id=i['id']),
            amount=i['amount']
        ) for i in validated_data.pop('ingredients')]
        RecipeIngredient.objects.bulk_create(recipeingredients)
        return super().update(recipe, validated_data)

    def get_ingredients(self, recipe):
        recipe_ingredients = {
            d.ingredient_id: d.amount for d in recipe.recipeingredients.all()}
        ingredients = recipe.ingredients.all()
        for ingredient in ingredients:
            ingredient.amount = recipe_ingredients[ingredient.id]
        serializer = IngredientAmountSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, recipe):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user.favorites.filter(recipe_id=recipe.id).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        if self.context['request'].user.is_authenticated:
            return self.context['request'].user.purchases.filter(recipe_id=recipe.id).exists()
        return False

    # def to_representation(self, instance):
    #     return BaseRecipeSerializer().to_representation(instance)