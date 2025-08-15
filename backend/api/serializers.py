import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, RecipeTag, RecipeIngredient


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Класс поля для аватара."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """Сериализатор данных модели FgUser."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        return obj.subscriptions.filter(
            id=self.context['request'].user.id
        ).exists()


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Recipe для Subscriptions."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор данных модели Subscriptions."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = SubscriptionRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        return obj.subscriptions.filter(
            id=self.context['request'].user.id
        ).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Ingredient."""

    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


# class IngredientToRecipeSerializer(serializers.ModelSerializer):
#     """Сериализатор данных модели Ingredient для Recipe."""
#
#     amount = serializers.IntegerField(read_only=True)
#
#     class Meta:
#         model = Ingredient
#         fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeInSerializer(serializers.ModelSerializer):
    """Сериализатор ввода данных модели Recipe."""

    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag, status = Tag.objects.get(**tag)
            RecipeTag.objects.create(tag=current_tag, recipe=recipe)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            RecipeIngredient.objects.create(
                ingredient=current_ingredient, recipe=recipe
            )
        return recipe


class RecipeOutSerializer(serializers.ModelSerializer):
    """Сериализатор вывода данных модели Recipe."""

    author = CustomUserSerializer()
    tags = TagSerializer(many=True,)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = ('id', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        return obj in self.context['request'].user.favorites.all()

    def get_is_in_shopping_cart(self, obj):
        return obj in self.context['request'].user.shopping_cart.all()

    def get_ingredients(self, obj):
        recipeingredients = {d.ingredient_id: d.amount for d in obj.recipeingredients.all()}
        ingredients = obj.ingredients.all()
        for ingredient in ingredients:
            ingredient.amount = recipeingredients[ingredient.id]
        serializer = IngredientSerializer(ingredients, many=True)
        return serializer.data
