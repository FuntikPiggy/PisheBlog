from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient

User = get_user_model()


class FoodgramUserSerializer(UserSerializer):
    """Сериализатор данных модели FoodgramUser."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = (*UserSerializer.Meta.fields, 'is_subscribed', 'avatar',)
        read_only_fields = fields

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        return user.is_authenticated and user.subscriptions_added.filter(
            author_id=author.id).exists()


class AvatarUserSerializer(UserSerializer):
    """Сериализатор данных модели FoodgramUser для смены аватара."""

    avatar = Base64ImageField(required=True,)

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('avatar',)


class BriefRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Recipe для избранного и корзины."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = fields


class UserSubscriptionsSerializer(FoodgramUserSerializer):
    """Сериализатор данных модели пользователя для модели Subscriptions."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        model = User
        fields = (*UserSerializer.Meta.fields, 'recipes',
                  'recipes_count', 'is_subscribed', 'avatar',)
        read_only_fields = fields

    def get_recipes(self, user):
        recipes = user.recipes.all()
        limit = self.context.get('request').query_params.get(
            'recipes_limit', None)
        if limit is not None:
            recipes = recipes[:int(limit)]
        return BriefRecipeSerializer(recipes, many=True).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор данных модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class RecipeSerializer(serializers.ModelSerializer):
    """Базовый класс сериализатора модели Recipe."""

    author = FoodgramUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True,)
    ingredients = IngredientSerializer(read_only=True, many=True,)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(validators=(MinValueValidator(1),))

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time',)
        required_fields = ('cooking_time',)

    def to_representation(self, recipe):
        amounts = dict(recipe.recipeingredients.values_list(
            'ingredient_id', 'amount',))
        recipe = super().to_representation(recipe)
        for ingredient in recipe['ingredients']:
            ingredient['amount'] = amounts[ingredient['id']]
        return recipe

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        return user.is_authenticated and user.favorites.filter(
            recipe_id=recipe.id).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        return user.is_authenticated and user.purchases.filter(
            recipe_id=recipe.id).exists()

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError('Добавьте изображение.')
        return image

    @staticmethod
    def create_update(recipe, tags, ingredients_amounts):
        recipe.tags.set(tags)
        recipe.ingredients.clear()
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe, ingredient_id=i[0], amount=i[1],
            ) for i in ingredients_amounts
        )
        return recipe

    def get_check_ingredients_and_tags(self):
        tag_ids = self.initial_data.get('tags', [])
        ingredients_amounts = [
            (i['id'], int(i['amount']))
            for i in self.initial_data.get('ingredients', [])
        ]
        if not ingredients_amounts:
            raise serializers.ValidationError('Не заданы продукты!')
        if len(ingredients_amounts) != len(set(ingredients_amounts)):
            raise serializers.ValidationError('Заданы одинаковые продукты!')
        if not all(Ingredient.objects.filter(id=i[0]).exists()
                   for i in ingredients_amounts):
            raise serializers.ValidationError('Отсутствующие в базе продукты!')
        if not all(i[1] > 0 for i in ingredients_amounts):
            raise serializers.ValidationError(
                'Количество продукта не может быть меньше 1!')
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError('Заданы одинаковые теги!')
        if len(tag_ids) == 0:
            raise serializers.ValidationError('Не заданы теги!')
        if not all(Tag.objects.filter(id=i).exists() for i in tag_ids):
            raise serializers.ValidationError('Отсутствующие в базе теги!')
        return tag_ids, ingredients_amounts

    def create(self, validated_data):
        tags, ingredients_amounts = self.get_check_ingredients_and_tags()
        recipe = super().create(validated_data)
        return self.create_update(recipe, tags, ingredients_amounts)

    def update(self, recipe, validated_data):
        tags, ingredients_amounts = self.get_check_ingredients_and_tags()
        recipe = self.create_update(recipe, tags, ingredients_amounts)
        return super().update(recipe, validated_data)
