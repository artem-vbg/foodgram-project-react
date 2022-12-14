# Generated by Django 2.2.16 on 2022-10-08 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20221008_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientamount',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='ingredientamount',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes_ingredients_list', to='recipes.Recipe', verbose_name='Рецепт'),
        ),
    ]
