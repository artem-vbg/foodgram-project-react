from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingListViewSet, SubscribeListViewSet, SubscribeView,
                    TagViewSet, UsersViewSet)

v1_router = DefaultRouter()
v1_router.register('users', UsersViewSet)
v1_router.register('recipes', RecipeViewSet, basename='recipes')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('tags', TagViewSet, basename='tag')


urlpatterns = [
    path(
        'users/subscriptions/',
        SubscribeListViewSet.as_view({'get': 'list'}),
        name='subscriptions'
        ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/<int:recipe_id>/shopping_list/',
        ShoppingListViewSet.as_view(),
        name='shopping_list'
        ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteViewSet.as_view(),
        name='favorite'
        ),
    path(
        'users/<int:user_id>/subscribe/',
        SubscribeView.as_view(),
        name='follow'
        ),
    path('', include(v1_router.urls)),
]
