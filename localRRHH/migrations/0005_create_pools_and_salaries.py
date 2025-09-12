from django.db import migrations, models


def create_pools(apps, schema_editor):
    NombrePool = apps.get_model('localRRHH', 'NombrePool')
    ApellidoPool = apps.get_model('localRRHH', 'ApellidoPool')
    SalarioOption = apps.get_model('localRRHH', 'SalarioOption')

    nombres = ['Ana','Luis','Jose','Maria','Pablo','Carmen','Juan','Marta','Diego','Laura','Raul','Nora','Elena','Carlos','Sofia','Pedro','Lucia','Andres','Rosa','Victor']
    apellidos = ['Garcia','Martinez','Lopez','Hernandez','Gonzalez','Perez','Sanchez','Ramirez','Torres','Flores','Diaz','Vargas','Rojas','Castro','Ortega','Molina','Silva','Cruz','Herrera','Mendez']

    for n in nombres:
        NombrePool.objects.get_or_create(nombre=n)
    for a in apellidos:
        ApellidoPool.objects.get_or_create(apellido=a)
    for s in range(800, 3001, 250):
        SalarioOption.objects.get_or_create(salario=s)


def drop_pools(apps, schema_editor):
    NombrePool = apps.get_model('localRRHH', 'NombrePool')
    ApellidoPool = apps.get_model('localRRHH', 'ApellidoPool')
    SalarioOption = apps.get_model('localRRHH', 'SalarioOption')
    NombrePool.objects.all().delete()
    ApellidoPool.objects.all().delete()
    SalarioOption.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('localRRHH', '0004_alter_apellidopool_options_alter_nombrepool_options_and_more'),
    ]

    operations = [
        migrations.RunPython(create_pools, reverse_code=drop_pools),
    ]
