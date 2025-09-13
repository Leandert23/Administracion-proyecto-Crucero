# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class RestaurantIngredientes(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    ingredientes = models.CharField(db_column='Ingredientes', max_length=40)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=20)  # Field name made lowercase.
    subtipo = models.CharField(db_column='Subtipo', max_length=40)  # Field name made lowercase.
    clase_alimenticia = models.CharField(db_column='Clase alimenticia', max_length=40)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'restaurant_ingredientes'


class RestaurantMenuDia1(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.IntegerField(db_column='Dia')  # Field name made lowercase.
    clasificacion = models.CharField(db_column='Clasificacion', max_length=80)  # Field name made lowercase.
    usos_platos = models.CharField(db_column='Usos / Platos', max_length=100)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000)  # Field name made lowercase.
    costo = models.FloatField(db_column='Costo')  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_menu_dia_1'


class RestaurantMenuDia2(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.IntegerField(db_column='Dia')  # Field name made lowercase.
    clasificacion = models.CharField(db_column='Clasificacion', max_length=80)  # Field name made lowercase.
    usos_platos = models.CharField(db_column='Usos / Platos', max_length=100)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000)  # Field name made lowercase.
    coste = models.FloatField(db_column='Coste')  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_menu_dia_2'


class RestaurantMenuDia3(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.IntegerField(db_column='Dia')  # Field name made lowercase.
    clasificacion = models.CharField(db_column='Clasificacion', max_length=100)  # Field name made lowercase.
    usos_platos = models.CharField(db_column='Usos / Platos', max_length=80)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000)  # Field name made lowercase.
    coste = models.FloatField(db_column='Coste')  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_menu_dia_3'


class RestaurantMenuDia4(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.IntegerField(db_column='Dia')  # Field name made lowercase.
    clasificacion = models.CharField(db_column='Clasificacion', max_length=80)  # Field name made lowercase.
    usos_platos = models.CharField(db_column='Usos / Platos', max_length=80)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000)  # Field name made lowercase.
    coste = models.FloatField(db_column='Coste')  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_menu_dia_4'


class RestaurantMenuDia5(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.IntegerField(db_column='Dia')  # Field name made lowercase.
    clasificacion = models.CharField(db_column='Clasificacion', max_length=100)  # Field name made lowercase.
    usos_platos = models.CharField(db_column='Usos / Platos', max_length=80)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000)  # Field name made lowercase.
    coste = models.FloatField(db_column='Coste')  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_menu_dia_5'


class RestaurantMenuDia6(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.IntegerField(db_column='Dia')  # Field name made lowercase.
    clasificacion = models.CharField(db_column='Clasificacion', max_length=100)  # Field name made lowercase.
    usos_platos = models.CharField(db_column='Usos / Platos', max_length=100)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000)  # Field name made lowercase.
    coste = models.FloatField(db_column='Coste')  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_menu_dia_6'


class RestaurantMenuDia7(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.IntegerField(db_column='Dia')  # Field name made lowercase.
    clasificacion = models.CharField(db_column='Clasificacion', max_length=100)  # Field name made lowercase.
    usos_platos = models.CharField(db_column='Usos / Platos', max_length=100)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000)  # Field name made lowercase.
    coste = models.FloatField(db_column='Coste')  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_menu_dia_7'


class RestaurantItaliano(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.CharField(db_column='Dia', max_length=10)  # Field name made lowercase.
    clasificacion = models.CharField(db_column='Clasificacion', max_length=100)  # Field name made lowercase.
    usos_platos = models.CharField(db_column='Usos / Platos', max_length=80)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000)  # Field name made lowercase.
    coste = models.FloatField(db_column='Coste')  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_italiano'


class RestaurantArabe(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.IntegerField(db_column='Dia')  # Field name made lowercase.
    clasificacion = models.CharField(db_column='Clasificacion', max_length=100)  # Field name made lowercase.
    usos_platos = models.CharField(db_column='Usos / Platos', max_length=80)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.CharField(db_column='Descripcion', max_length=100)  # Field name made lowercase.
    coste = models.FloatField(db_column='Coste')  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_arabe'


class RestaurantVinos(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.IntegerField(db_column='Dia')  # Field name made lowercase.
    clasificacion = models.CharField(db_column='Clasificacion', max_length=80)  # Field name made lowercase.
    marca = models.CharField(db_column='Marca', max_length=80)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000)  # Field name made lowercase.
    presentacion = models.CharField(db_column='Presentacion', max_length=1000)  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_vinos'


class RestaurantCartaEspecial(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    dia = models.IntegerField(db_column='Dia')
    clasificacion = models.CharField(db_column='Clasificacion', max_length=80)  # Field name made lowercase.
    usos_platos = models.CharField(db_column='Usos / Platos', max_length=100)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000)  # Field name made lowercase.
    coste = models.FloatField(db_column='Coste')  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_carta_especial'


class RestaurantMenuFijo(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.IntegerField(db_column='Dia')  # Field name made lowercase.
    clasificacion = models.CharField(db_column='Clasificacion', max_length=100)  # Field name made lowercase.
    usos_platos = models.CharField(db_column='Usos / Platos', max_length=100)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.CharField(db_column='Descripcion', max_length=1000)  # Field name made lowercase.
    coste = models.FloatField(db_column='Coste')  # Field name made lowercase.
    precio = models.FloatField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_menu_fijo'


class RestaurantBuffet(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    dia = models.TextField(db_column='Dia')  # Field name made lowercase.
    clasificacion = models.TextField(db_column='Clasificacion')  # Field name made lowercase.
    usos_platos = models.TextField(db_column='Usos / Platos')  # Field name made lowercase. Field renamed to remove unsuitable characters.
    descripcion = models.TextField(db_column='Descripcion')  # Field name made lowercase.
    coste = models.IntegerField(db_column='Coste')  # Field name made lowercase.
    precio = models.IntegerField(db_column='Precio')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'restaurant_buffet'


# Note: Table 'restaurant_platillos_ingredientes' could not be inspected.
# The error was: Table restaurant_platillos_ingredientes does not exist (empty pragma).


class RestaurantProducts(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    ingredientes = models.CharField(db_column='Ingredientes', max_length=80)  # Field name made lowercase.
    tipo = models.CharField(db_column='Tipo', max_length=80)  # Field name made lowercase.
    subtipo = models.CharField(db_column='Subtipo', max_length=80)  # Field name made lowercase.
    clase_alimenticia = models.CharField(db_column='Clase alimenticia', max_length=80)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'restaurant_products'
