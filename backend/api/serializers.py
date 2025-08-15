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

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Ingredient для Recipe."""

    # id = serializers.SerializerMethodField()
    # name = serializers.SerializerMethodField()
    # measurement_unit = serializers.SerializerMethodField()
    # amount = serializers.SerializerMethodField()
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    # def get_id(self, obj):
    #     return obj.id
    #
    # def get_name(self, obj):
    #     return obj.name
    #
    # def get_measurement_unit(self, obj):
    #     return obj.measurement_unit
    # def to_representation(self, instance):
    #     self._context["request"] = self.parent.context["request"]
    #     return super().to_representation(instance)

    # def get_amount(self, obj):
    # #     # a = self.amount
    # #     # b = obj.ingredients_amount.get(recipe_id=obj.id)
    #     asd = (f'{obj.id=}')
    # #     c = obj.ingredients_amount.get(recipe_id=obj.id).amount
    #     return obj.ingredients_amount.get(recipe_id=obj.id).amount


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


# class Ingr(serializers.Field):
#     def to_representation(self, value):
#         a = 1
#         return value
#     def to_internal_value(self, data):
#         return data



class RecipeOutSerializer(serializers.ModelSerializer):
    """Сериализатор вывода данных модели Recipe."""

    author = CustomUserSerializer()
    tags = TagSerializer(many=True,)
    # ingredients = Ingr()
    ingredients = serializers.SerializerMethodField(read_only=True)
    # ingredients = IngredientToRecipeSerializer(many=True,)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        return True

    def get_is_in_shopping_cart(self, obj):
        return True

    def get_ingredients(self, obj):
        recipeingredients = {d.ingredient_id: d.amount for d in obj.recipeingredients.all()}
        # ingredients = Ingredient.objects.filter(recipeingredients__recipe_id = obj.id)
        ingredients = obj.ingredients.all()
        # ingredients = self.context['queryset'][obj.id].values('ingredient__id', 'ingredient__name', 'ingredient__measurement_unit', 'ingredient__amount')
        # ingredients = self.context['queryset'][obj.id].ingredients.all().annotate(amount='ingredient_amount.amount')


        for ingredient in ingredients:
            # psc = RecipeIngredient.objects.get(recipe_id = obj.id, ingredient_id = ingredient.id)
            # ingredient.amount = psc.amount
            ingredient.amount = recipeingredients[ingredient.id]

        serializer = IngredientToRecipeSerializer(ingredients, many=True)

        return serializer.data
