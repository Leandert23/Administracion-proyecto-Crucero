# Generated manually for adding fecha_inicio and fecha_fin fields to Ruta model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creador_embarcaciones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruta',
            name='fecha_inicio',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de inicio de la ruta'),
        ),
        migrations.AddField(
            model_name='ruta',
            name='fecha_fin',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha de fin de la ruta'),
        ),
    ]
