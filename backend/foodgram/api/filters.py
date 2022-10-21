import django_filters
from recipes.models import (Ingredient, Favorite, Recipe,
                            ShoppingCart, Tag)
from django_filters.rest_framework import FilterSet, filters


class RecipeFilterSet(FilterSet):

    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    is_favorited = django_filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited',
    )

    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'is_favorited']

    def filter_is_favorited(self, queryset, name, tags):
        user = self.request.user
        fav_recipes = Favorite.objects.filter(user=user).values('recipe')
        return queryset.filter(id__in=fav_recipes)

    def filter_is_in_shopping_cart(self, queryset, name, tags):
        user = self.request.user
        recipes = ShoppingCart.objects.filter(user=user).values('recipe')
        return queryset.filter(id__in=recipes)


class IngredientSearchFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
