# Manual bootstrap to fix missing legacy tables before 0012
from django.db import migrations

SQL_CREATE_ING = (
    'CREATE TABLE IF NOT EXISTS "restaurant_ingrediente" ('
    '"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,'
    '"nombre" varchar(100) NOT NULL,'
    '"precio" numeric NOT NULL DEFAULT 0,'
    '"unidad" varchar(20) NOT NULL,'
    '"descripcion" text NOT NULL DEFAULT "",'
    '"stock_disponible" numeric NOT NULL DEFAULT 0,'
    '"stock_minimo" numeric NOT NULL DEFAULT 0,'
    '"created_at" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP'
    ');'
)

SQL_CREATE_ING_PLAT = (
    'CREATE TABLE IF NOT EXISTS "restaurant_ingredienteplatillo" ('
    '"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,'
    '"cantidad" numeric NOT NULL DEFAULT 0,'
    '"unidad" varchar(20) NOT NULL,'
    '"ingrediente_id" integer NOT NULL,'
    '"platillo_id" integer NOT NULL'
    ');'
)

class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0011_add_cruise_day_to_invoice_and_buffet'),
    ]

    operations = [
        migrations.RunSQL(SQL_CREATE_ING),
        migrations.RunSQL(SQL_CREATE_ING_PLAT),
    ]
