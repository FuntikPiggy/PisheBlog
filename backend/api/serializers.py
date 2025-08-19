from functools import wraps
import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, RecipeTag, RecipeIngredient

User = get_user_model()


def manytomany_setter_deleter(func):
    """Декоратор для методов получения значений для полей
    is_subscribed, is_favorited и is_in_shopping_cart."""
    @wraps(func)
    def wrapper(self, obj):
        if self.context['request'].user.is_authenticated:
            return func(self, obj).filter(id=obj.id).exists()
        return False
    return wrapper


class IsSubscribedMixin(metaclass=serializers.SerializerMetaclass):
    """Миксин подписок пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar']

    @manytomany_setter_deleter
    def get_is_subscribed(self, user):
        return self.context['request'].user.subscriptions


class Base64ImageField(serializers.ImageField):
    """Класс поля для изображений."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(IsSubscribedMixin, UserSerializer):
    """Сериализатор данных модели FgUser."""

    avatar = Base64ImageField(required=False, allow_null=True)


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Recipe для Subscriptions."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionsSerializer(IsSubscribedMixin, UserSerializer):
    """Сериализатор данных модели Subscriptions."""

    recipes = serializers.SerializerMethodField('paginated_recipes')
    recipes_count = serializers.SerializerMethodField()

    class Meta(IsSubscribedMixin.Meta):
        fields = IsSubscribedMixin.Meta.fields + ['recipes', 'recipes_count']

    def paginated_recipes(self, user):
        return SubscriptionRecipeSerializer(Paginator(
            user.recipes.all(),
            self.context['request'].query_params.get('recipes_limit', 3)
        ).page(1), many=True,).data

    def get_recipes_count(self, user):
        return user.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)
        read_only_fields = ('id', 'name', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        # read_only_fields = ('id', 'name', 'measurement_unit',)


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Ingredient для
     сериализатора вывода модели Recipe."""

    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)
        # read_only_fields = ('id', 'name', 'measurement_unit', 'amount',)


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый класс для сериализаторов модели Recipe."""

    author = CustomUserSerializer(read_only=True,)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time',)
        read_only_fields = ('id', 'author', 'ingredients', 'tags',
                            'is_favorited', 'is_in_shopping_cart',)

    def get_ingredients(self, recipe):
        recipe_ingredients = {
            d.ingredient_id: d.amount for d in recipe.recipeingredients.all()}
        ingredients = recipe.ingredients.all()
        for ingredient in ingredients:
            ingredient.amount = recipe_ingredients[ingredient.id]
        serializer = IngredientToRecipeSerializer(ingredients, many=True)
        return serializer.data

    @manytomany_setter_deleter
    def get_is_favorited(self, recipe):
        return self.context['request'].user.favorites

    @manytomany_setter_deleter
    def get_is_in_shopping_cart(self, recipe):
        return self.context['request'].user.shopping_cart


class RecipeInSerializer(BaseRecipeSerializer):
    """Сериализатор ввода данных модели Recipe."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, default=TagSerializer(), read_only=True)

    class Meta(BaseRecipeSerializer.Meta):
        model = Recipe

    def create(self, validated_data):
        tags_ids = validated_data.pop('tags', [])
        ingredients_amounts = self.initial_data['ingredients']
        recipe = Recipe.objects.create(**validated_data)
        for tag_id in tags_ids:
            tag = Tag.objects.get(id=tag_id)
            RecipeTag.objects.create(tag=tag, recipe=recipe)
        for ingredient_amount in ingredients_amounts:
            ingredient = Ingredient.objects.get(id=ingredient_amount['id'])
            amount = ingredient_amount['amount']
            RecipeIngredient.objects.create(
                ingredient=ingredient, recipe=recipe, amount=amount,
            )
        return recipe

    def update(self, recipe, validated_data):
        new_tags_ids = set(validated_data.pop('tags'))
        old_tags_ids = set(recipe.tags.values_list('id', flat=True))
        new_ids_amounts = {
            i['id']: i['amount'] for i in validated_data.pop('ingredients')}
        old_ingredients_ids = set(
            recipe.ingredients.values_list('id', flat=True))
        recipe.save()
        [recipe.tags.remove(tag) for tag in old_tags_ids - new_tags_ids]
        [recipe.tags.add(tag) for tag in new_tags_ids - old_tags_ids]
        [recipe.ingredients.remove(ingredient)
         for ingredient in old_ingredients_ids - set(new_ids_amounts.keys())]
        [recipe.ingredients.add(
            i, through_defaults={'amount': new_ids_amounts[i]})
         for i in new_ids_amounts.keys() - old_ingredients_ids]
        return recipe


class RecipeOutSerializer(BaseRecipeSerializer):
    """Сериализатор вывода данных модели Recipe."""

    tags = TagSerializer(read_only=True, many=True)

    class Meta(BaseRecipeSerializer.Meta):
        model = Recipe
