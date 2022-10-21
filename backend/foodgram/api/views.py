from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from users.models import CustomUser, Follow
from recipes.models import (Ingredient, IngredientAmount, Favorite, Recipe,
                            ShoppingCart, Tag)
from rest_framework import permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilterSet
from .permissions import IsAdmin, IsAuthorOrAdmin, IsSuperuser
from .serializers import (FavoriteCreateSerializer, FavoriteSerializer,
                          FollowCreateSerializer, FollowSerializer,
                          IngredientSerializer, ListRecipeSerializer,
                          RecipeSerializer, ShoppingCartCreateSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserSerializer)
from .utils import DataMixin, download_file_response


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    lookup_field = 'username'
    permission_classes = (permissions.IsAuthenticated, IsSuperuser | IsAdmin,)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        methods=['get', 'patch'],
        url_path='me')
    def get_or_update_self(self, request):
        if request.method != 'GET':
            serializer = self.get_serializer(
                instance=request.user,
                data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(
                request.user,
                many=False)
            return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdmin,)
    queryset = Recipe.objects.all()
    serializer_class = ListRecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return RecipeSerializer
        return ListRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user_id": self.request.user})
        return context

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        methods=['get', ])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=user).values(
            'ingredient__name', 'ingredient__measurement_unit').order_by(
                'ingredient__name').annotate(ingredient_total=Sum('amount'))

        lines = []

        for ingredient in ingredients:
            lines.append(
                f'{ingredient["ingredient__name"]}'
                + f' – {ingredient["ingredient_total"]}'
                + f'{ingredient["ingredient__measurement_unit"]}.\n'
            )
        return download_file_response(lines, 'shop_list.txt')


class IngredientViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdmin,)
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientSearchFilter
    search_fields = ('^name',)


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrAdmin,)
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ShoppingCartViewSet(DataMixin, views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TagSerializer
    pagination_class = None

    def post(self, request, recipe_id):
        return self.add_to_universal_method(
            ShoppingCart, ShoppingCartCreateSerializer,
            ShoppingCartSerializer, recipe_id)

    def delete(self, request, recipe_id):
        return self.del_from_universal_method(
            ShoppingCart, recipe_id)


class FavoriteViewSet(DataMixin, views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FavoriteSerializer
    pagination_class = None

    def post(self, request, recipe_id):
        return self.add_to_universal_method(
            Favorite, FavoriteCreateSerializer,
            FavoriteSerializer, recipe_id)

    def delete(self, request, recipe_id):
        return self.del_from_universal_method(
            Favorite, recipe_id)


class SubscribeView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, user_id):
        user = self.request.user
        author = get_object_or_404(CustomUser, id=user_id)
        serializer = FollowCreateSerializer(
            data={'user': user.id, 'author': user_id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        follow = get_object_or_404(
            Follow,
            user=user,
            author=author
        )
        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        user = request.user
        author = get_object_or_404(CustomUser, id=user_id)
        follow = get_object_or_404(Follow, user=user, author=author)
        follow.delete()
        return Response(
            'Удаление прошло успешно!', status=status.HTTP_204_NO_CONTENT
        )


class SubscribeListViewSet(viewsets.ModelViewSet, PageNumberPagination):
    permission_classes = (IsAuthorOrAdmin,)
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def list(self, request, *args, **kwargs):
        user = self.request.user
        subscriptions = user.follower.all()
        page = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
