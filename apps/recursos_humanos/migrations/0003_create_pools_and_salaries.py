# Generated migration to add NombrePool, ApellidoPool, SalarioOption and populate them
from django.db import migrations, models


def create_initial_pools(apps, schema_editor):
    NombrePool = apps.get_model('localRRHH', 'NombrePool')
    ApellidoPool = apps.get_model('localRRHH', 'ApellidoPool')
    SalarioOption = apps.get_model('localRRHH', 'SalarioOption')

    nombres = ['Ana','Luis','Jose','Maria','Pablo','Carmen','Juan','Marta','Diego','Laura','Raul','Nora','Elena','Carlos','Sofia','Pedro','Lucia','Andres','Rosa','Victor']
    apellidos = ['Garcia','Martinez','Lopez','Hernandez','Gonzalez','Perez','Sanchez','Ramirez','Torres','Flores','Diaz','Vargas','Rojas','Castro','Ortega','Molina','Silva','Cruz','Herrera','Mendez']
    salarios = [s for s in range(800, 3001, 250)]

    for n in nombres:
        NombrePool.objects.create(nombre=n)
    for a in apellidos:
        ApellidoPool.objects.create(apellido=a)
    for s in salarios:
        SalarioOption.objects.create(salario=s)


class Migration(migrations.Migration):

    dependencies = [
        ('localRRHH', '0002_amonestacion_personal_delete_item_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NombrePool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='ApellidoPool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('apellido', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='SalarioOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salario', models.PositiveIntegerField()),
            ],
        ),
        migrations.RunPython(create_initial_pools),
    ]
