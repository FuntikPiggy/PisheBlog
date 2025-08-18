import base64
from functools import wraps

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
        ).page(1),many=True,).data

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
        read_only_fields = ('id', 'name', 'measurement_unit',)


# class MeasureSerializer(serializers.ModelSerializer):
#     """Класс поля количества ингредиента."""
#
#     def to_internal_value(self, data):
#         if not isinstance(data, int) or data < 1:
#             raise serializers.ValidationError('Количество должно быть целым числом > 0')
#         format, imgstr = data.split(';base64,')
#         ext = format.split('/')[-1]
#         data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
#         return super().to_internal_value(data)



class IngredientToRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Ingredient для Recipe."""

    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)
        read_only_fields = ('id', 'name', 'measurement_unit', 'amount',)

# class IngredientToRecipeSerializer(serializers.Serializer):
#     """Сериализатор данных модели Ingredient для Recipe."""
#
#     id = serializers.IntegerField()
#     amount = serializers.IntegerField()
#     #
#     # class Meta:
#     #     fields = ('id', 'amount',)
#
#     # def get_amount(self, ingredient):
#     #     a = 1
#     #     return ingredient.recipeingredients.amount


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый класс для сериализаторов модели Recipe."""

    author = CustomUserSerializer(read_only=True,)
    tags = TagSerializer(many=True,)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(required=False, allow_null=True)

    @manytomany_setter_deleter
    def get_is_favorited(self, recipe):
        return self.context['request'].user.favorites

    @manytomany_setter_deleter
    def get_is_in_shopping_cart(self, recipe):
        return self.context['request'].user.shopping_cart


class RecipeInSerializer(serializers.ModelSerializer):
    """Сериализатор ввода данных модели Recipe."""

    # author = CustomUserSerializer(read_only=True,)
    # author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True, default=TagSerializer())
    image = Base64ImageField()
    # ingredients = IngredientSerializer(many=True,)
    ingredients = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',)

    def get_ingredients(self, recipe):
        recipe_ingredients = {d.ingredient_id: d.amount for d in recipe.recipeingredients.all()}
        ingredients = recipe.ingredients.all()
        for ingredient in ingredients:
            ingredient.amount = recipe_ingredients[ingredient.id]
        serializer = IngredientToRecipeSerializer(ingredients, many=True)
        return serializer.data

    def create(self, validated_data):
        tags_ids = self.initial_data['tags']
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

    def update(self, validated_data):
        tags_statuses = validated_data.pop('tags')
        ingredients_statuses = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag_status in tags_statuses:
            tag, status = Tag.objects.get(**tag_status)
            RecipeTag.objects.create(tag=tag, recipe=recipe)
        for ingredient_status in ingredients_statuses:
            ingredient, status = Ingredient.objects.get(**ingredient_status)
            RecipeIngredient.objects.create(
                ingredient=ingredient, recipe=recipe
            )
        return recipe


class RecipeOutSerializer(BaseRecipeSerializer):
    """Сериализатор вывода данных модели Recipe."""

    # ingredients = IngredientToRecipeSerializer(many=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    # tags = TagSerializer(many=True,)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    # tags = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited','is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time',)
        read_only_fields = ('id', 'author', 'ingredients', 'tags',
                            'is_favorited', 'is_in_shopping_cart',)

    def get_ingredients(self, recipe):
        recipe_ingredients = {d.ingredient_id: d.amount for d in recipe.recipeingredients.all()}
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
