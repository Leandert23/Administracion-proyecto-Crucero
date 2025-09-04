import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aplicaciones', '0005_remove_cuarto_tipo_alter_cuarto_numero'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuarto',
            name='paciente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='aplicaciones.paciente'),
        ),
    ]
