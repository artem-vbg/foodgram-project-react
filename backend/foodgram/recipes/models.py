from django.core.validators import MinValueValidator
from django.db import models
from users.models import CustomUser


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        help_text='Укажите название ингредиента'
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=200,
        help_text='Укажите единицу измерения'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField('Тег', max_length=200, unique=True,)
    color = models.CharField(
        max_length=7,
        default='#ffffff',
        unique=True,
        verbose_name=(u'Color'),
        help_text=(u'HEX color, as #RRGGBB')
    )
    slug = models.SlugField("Slug", unique=True, max_length=200)

    class Meta:
        ordering = ['id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        help_text='Добавьте название рецепта'
    )
    image = models.ImageField(
        null=True,
        upload_to='image/',
        verbose_name='Изображение',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Добавьте описание рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                1,
                message='Минимальное время приготовления 1 мин.'
            ),
        ],
        help_text='Укажите время приготовления',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=True,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        through='TagRecipe',
        related_name='recipes',
        verbose_name='Теги',
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipes_ingredients_list',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipes_ingredients_list',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество игредиентов'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Количество игредиентов',
        verbose_name_plural = 'Количества игредиентов'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredient'],
            name='recipe_ingredient_unique'
        )]

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Теги в рецепте',
        verbose_name_plural = 'Теги в рецептах'
        constraints = [models.UniqueConstraint(
            fields=['tag', 'recipe'],
            name='recipe_tag_unique'
        )]

    def __str__(self):
        return f'{self.tag.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Покупатель'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=True,
        related_name='shopping_cart',
        verbose_name='Товар'
        )

    class Meta:
        ordering = ['id']
        verbose_name = 'Список покупок',
        verbose_name_plural = 'Списки покупок'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='list_item_unique'
        )]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='Рецепт в избранном'
        )

    class Meta:
        ordering = ['id']
        verbose_name = 'Избранное',
        verbose_name_plural = 'Избранные'
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='favorite_recipe_unique'
        )]

    def __str__(self):
        return (f'{self.user.username} '
                + f'добавил в избранное {self.recipe.name}')
