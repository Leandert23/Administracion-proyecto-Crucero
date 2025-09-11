# Generated manually to fix migration conflicts

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0007_platillo_restaurantes'),
    ]

    # Esta migración originalmente recreaba modelos ya creados en 0002, causando
    # errores "table ... already exists". Se convierte en NO-OP para permitir
    # continuar la cadena (0009 depende de 0008) sin re-crear tablas.
    operations = []
