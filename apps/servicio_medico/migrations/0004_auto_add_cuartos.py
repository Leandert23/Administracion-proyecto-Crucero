from django.db import migrations

def crear_cuartos(apps, schema_editor):
    Cuarto = apps.get_model('aplicaciones', 'cuarto')
    for numero in ['1', '2', '3']:
        Cuarto.objects.get_or_create(numero=numero)

class Migration(migrations.Migration):

    dependencies = [
        ('aplicaciones', '0003_rename_apellido_paciente_primer_apellido_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_cuartos),
    ]
