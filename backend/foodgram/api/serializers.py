from drf_extra_fields.fields import Base64ImageField
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag, TagRecipe)
from users.models import CustomUser, Follow

from .utils import DataSerializerMixin


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'first_name',
            'last_name',
            'username',
            'id',
            'email',)
        model = CustomUser
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = TagRecipe
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ['id', 'name', 'measurement_unit', 'amount']


class ListRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipes_ingredients_list',
        many=True,
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time'
                  )

    def get_is_favorited(self, obj):
        user = self.context.get('user_id')
        recipe = obj.id
        return Favorite.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("user_id")
        recipe = obj.id
        return ShoppingCart.objects.filter(
            recipe=recipe, user=user).exists()


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        source='tagrecipe_set',
        queryset=Tag.objects.all(),
        many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipes_ingredients_list',
        many=True,
        required=False
    )
    image = Base64ImageField(
        max_length=None, use_url=True,
    )
    cooking_time = serializers.IntegerField()

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )
        model = Recipe

    def validate_ingredients(self, data):
        ingredients_list = []
        ingredients = data
        if not ingredients:
            raise serializers.ValidationError(
                'Нужно выбрать минимум 1 ингредиент'
            )
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    'Количество ингридиентов должно быть положительным'
                )
            check_id = ingredient['ingredient']['id']
            if check_id in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты в рецепте дублируются'
                )
            ingredients_list.append(check_id)
        return data

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError(
                'Минимальное время приготовления 1 мин'
            )
        return data

    def validate_tags(self, data):
        tags = data
        if not tags:
            raise serializers.ValidationError('Нужно выбрать минимум 1 тег')
        return data

    def create_recipe_ingredient_and_tag(self, ingredients, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient,
                id=ingredient.get('ingredient').get('id')
            )
            amount = ingredient.get('amount')
            if IngredientAmount.objects.filter(
                recipe=recipe, ingredient=current_ingredient
            ).exists():
                amount += F('amount')
            IngredientAmount.objects.update_or_create(
                ingredient=current_ingredient,
                recipe=recipe,
                defaults={'amount': amount}
            )

    def create(self, validated_data):
        author = self.context.get('user_id')
        tags = validated_data.pop('tagrecipe_set')
        ingredients = validated_data.pop('recipes_ingredients_list')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.save()
        self.create_recipe_ingredient_and_tag(ingredients, tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tagrecipe_set')
        ingredients = validated_data.pop('recipes_ingredients_list')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_recipe_ingredient_and_tag(
            ingredients=ingredients, tags=tags, recipe=instance)
        return instance

    def to_representation(self, instance):
        return ListRecipeSerializer(
            instance,
            context={
                "user_id": self.context.get('user_id')
            }
        ).data


class ShoppingCartCreateSerializer(DataSerializerMixin,
                                   serializers.ModelSerializer):
    recipe = serializers.IntegerField(source='recipe.id')
    user = serializers.IntegerField(source='user.id')

    class Meta:
        model = ShoppingCart
        fields = ['recipe', 'user']

    def create(self, validated_data):
        return self.create_serializer(
            Recipe, ShoppingCart, validated_data)

    def validate(self, data):
        return self.validate_serializer(
            ShoppingCart, data)


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(read_only=True, source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time']


class FavoriteCreateSerializer(DataSerializerMixin,
                               serializers.ModelSerializer):
    recipe = serializers.IntegerField(source='recipe.id')
    user = serializers.IntegerField(source='user.id')

    class Meta:
        model = Favorite
        fields = ['recipe', 'user']

    def create(self, validated_data):
        return self.create_serializer(
            Recipe, Favorite, validated_data)

    def validate(self, data):
        return self.validate_serializer(
            Favorite, data)


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(read_only=True, source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowCreateSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    author = serializers.IntegerField(source='author.id')

    class Meta:
        model = Follow
        fields = ['user', 'author']

    def create(self, validated_data):
        author = get_object_or_404(
            CustomUser,
            pk=validated_data.get('author').get('id')
        )
        user = validated_data.get('user')
        return Follow.objects.create(user=user, author=author)

    def validate(self, data):
        if Follow.objects.filter(
                author__id=data.get('author').get('id'),
                user__id=data.get('user').get('id')).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора'
            )
        return data


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = ListRecipeSerializer(
        source='author.recipes',
        many=True,
        data=Recipe.objects.all(),
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]

    def get_is_subscribed(self, obj):
        author = obj.author
        user = obj.user
        return Follow.objects.filter(author=user, user=author).exists()

    def get_recipes_count(self, obj):
        author = obj.author
        count = Recipe.objects.filter(author=author).count()
        return count
