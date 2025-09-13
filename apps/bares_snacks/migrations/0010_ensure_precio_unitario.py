from django.db import migrations, connection


def ensure_precio_unitario(apps, schema_editor):
    table = 'bares_snacks_detallepedido'
    with connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info('{table}')")
        cols = [r[1] for r in cursor.fetchall()]
        if 'precio_unitario' not in cols:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN precio_unitario DECIMAL(10,2) NOT NULL DEFAULT 0")
            except Exception:
                pass


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('bares_snacks', '0009_rebuild_detallepedido_table'),
    ]

    operations = [
        migrations.RunPython(ensure_precio_unitario, noop),
    ]
