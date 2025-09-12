from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('restaurant', '0010_serviceinvoice_alter_restaurante_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceinvoice',
            name='cruise_day',
            field=models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Día Crucero'),
        ),
        migrations.AddField(
            model_name='buffetbulkrecord',
            name='cruise_day',
            field=models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Día Crucero'),
        ),
    ]
