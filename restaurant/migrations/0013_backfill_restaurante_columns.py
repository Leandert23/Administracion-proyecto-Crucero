from django.db import migrations, connection


def add_missing_restaurante_cols(apps, schema_editor):
    table = 'restaurant_restaurante'
    with connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = {row[1] for row in cursor.fetchall()}

        def add(col_name, sql_def):
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {sql_def}")

        if 'largo' not in cols:
            add('largo', 'NUMERIC NULL')
        if 'ancho' not in cols:
            add('ancho', 'NUMERIC NULL')
        if 'area_total' not in cols:
            add('area_total', 'NUMERIC NULL')
        if 'ubicacion' not in cols:
            add('ubicacion', "TEXT NOT NULL DEFAULT ''")
        if 'descripcion' not in cols:
            add('descripcion', "TEXT NOT NULL DEFAULT ''")
        if 'horario_apertura' not in cols:
            add('horario_apertura', 'TEXT NULL')
        if 'horario_cierre' not in cols:
            add('horario_cierre', 'TEXT NULL')
        if 'activo' not in cols:
            add('activo', 'INTEGER NOT NULL DEFAULT 1')


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0012_request_remove_ingrediente_created_at_and_more'),
    ]

    operations = [
        migrations.RunPython(add_missing_restaurante_cols, migrations.RunPython.noop),
    ]
