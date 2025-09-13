from django.db import migrations, connection


def add_precio_unitario(apps, schema_editor):
    table = 'bares_snacks_detallepedido'
    with connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info('{table}')")
        cols = [r[1] for r in cursor.fetchall()]
        if 'precio_unitario' not in cols:
            try:
                cursor.execute(
                    f"ALTER TABLE {table} ADD COLUMN precio_unitario DECIMAL(10,2) NOT NULL DEFAULT 0"
                )
            except Exception:
                # Ignore if fails (older SQLite) – next rebuild migration would be needed
                pass


class Migration(migrations.Migration):
    dependencies = [
        ('bares_snacks', '0010_ensure_precio_unitario'),
    ]

    operations = [
        migrations.RunPython(add_precio_unitario, migrations.RunPython.noop),
    ]
