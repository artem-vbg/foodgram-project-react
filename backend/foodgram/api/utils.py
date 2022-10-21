from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from recipes.models import Recipe
from rest_framework.response import Response


def download_file_response(list_to_download, filename):
    response = HttpResponse(list_to_download, 'Content-Type: text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


class DataMixin:

    def add_to_universal_method(self, model, serializer_crtd_cls,
                                serializer_cls, recipe_id):
        value = get_object_or_404(Recipe, pk=recipe_id)
        user = self.request.user
        serializer = serializer_crtd_cls(
            data={'recipe': recipe_id, 'user': user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        obj_data = get_object_or_404(
            model,
            recipe=value,
            user=user,
        )
        serializer = serializer_cls(obj_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def del_from_universal_method(self, model, recipe_id):
        user = self.request.user
        value = get_object_or_404(Recipe, pk=recipe_id)
        obj_data = get_object_or_404(
            model,
            recipe=value,
            user=user
        )
        obj_data.delete()
        return Response(
            'Удаление прошло успешно!', status=status.HTTP_204_NO_CONTENT
        )


class DataSerializerMixin:

    def create_serializer(self, model, serializer_cls, validated_data):
        recipe = get_object_or_404(
            model,
            pk=validated_data.get('recipe').get('id')
        )
        user = validated_data.get('user')
        return serializer_cls.objects.create(recipe=recipe, user=user)

    def validate_serializer(self, serializer_cls, data):
        if serializer_cls.objects.filter(
                recipe__id=data.get('recipe').get('id'),
                user__id=data.get('user').get('id')).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен'
            )
        return data
