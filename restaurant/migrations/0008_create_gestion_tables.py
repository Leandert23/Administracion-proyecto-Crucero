# Generated manually to fix migration conflicts

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0007_platillo_restaurantes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingrediente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre del Ingrediente')),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio por Unidad')),
                ('unidad', models.CharField(choices=[('kg', 'Kilogramo'), ('g', 'Gramo'), ('l', 'Litro'), ('ml', 'Mililitro'), ('unidad', 'Unidad'), ('taza', 'Taza'), ('cucharada', 'Cucharada'), ('cucharadita', 'Cucharadita')], max_length=20, verbose_name='Unidad de Medida')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('stock_disponible', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Stock Disponible')),
                ('stock_minimo', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Stock Mínimo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
            ],
            options={
                'verbose_name': 'Ingrediente',
                'verbose_name_plural': 'Ingredientes',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='IngredientePlatillo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Cantidad')),
                ('unidad', models.CharField(choices=[('kg', 'Kilogramo'), ('g', 'Gramo'), ('l', 'Litro'), ('ml', 'Mililitro'), ('unidad', 'Unidad'), ('taza', 'Taza'), ('cucharada', 'Cucharada'), ('cucharadita', 'Cucharadita')], max_length=20, verbose_name='Unidad')),
                ('ingrediente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurant.ingrediente', verbose_name='Ingrediente')),
                ('platillo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredientes', to='restaurant.platillo', verbose_name='Platillo')),
            ],
            options={
                'verbose_name': 'Ingrediente del Platillo',
                'verbose_name_plural': 'Ingredientes de Platillos',
                'unique_together': {('platillo', 'ingrediente')},
            },
        ),
    ]
