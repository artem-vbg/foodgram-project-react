# Generated by Django 2.2.16 on 2022-09-09 15:33

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': ('Избранное',),
                'verbose_name_plural': 'Избранные',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Укажите название ингредиента', max_length=200, verbose_name='Название')),
                ('measurement_unit', models.CharField(help_text='Укажите единицу измерения', max_length=200, verbose_name='Единицы измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='IngredientAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(verbose_name='Количество игредиентов')),
            ],
            options={
                'verbose_name': ('Количество игредиентов',),
                'verbose_name_plural': 'Количества игредиентов',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Добавьте название рецепта', max_length=200, verbose_name='Название')),
                ('image', models.ImageField(upload_to='image/', verbose_name='Изображение')),
                ('text', models.TextField(help_text='Добавьте описание рецепта', verbose_name='Описание')),
                ('cooking_time', models.PositiveIntegerField(help_text='Укажите время приготовления', validators=[django.core.validators.MinValueValidator(1, message='Минимальное время приготовления 1 мин.')], verbose_name='Время приготовления (в минутах)')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Тег')),
                ('color', models.CharField(default='#ffffff', help_text='HEX color, as #RRGGBB', max_length=7, unique=True, verbose_name='Color')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Slug')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='TagRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe', verbose_name='Рецепт')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Tag', verbose_name='Тег')),
            ],
            options={
                'verbose_name': ('Теги в рецепте',),
                'verbose_name_plural': 'Теги в рецептах',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe', verbose_name='Товар')),
            ],
            options={
                'verbose_name': ('Список покупок',),
                'verbose_name_plural': 'Списки покупок',
                'ordering': ['id'],
            },
        ),
    ]
