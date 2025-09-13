from django.db import migrations, connection


def forward(apps, schema_editor):
    table = 'bares_snacks_detallepedido'
    # Inspect columns
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info('%s')" % table)
        cols = [row[1] for row in cursor.fetchall()]

        # If legacy menu_id exists and producto_id doesn't, rename it to producto_id
        if 'menu_id' in cols and 'producto_id' not in cols:
            try:
                cursor.execute("ALTER TABLE %s RENAME COLUMN menu_id TO producto_id" % table)
            except Exception:
                # Best-effort; on very old SQLite this may fail
                pass
        elif 'menu_id' in cols and 'producto_id' in cols:
            # If both exist, try to drop the legacy menu_id
            try:
                cursor.execute("ALTER TABLE %s DROP COLUMN menu_id" % table)
            except Exception:
                # DROP COLUMN not supported in older SQLite; ignore
                pass

        # Ensure precio_unitario column exists
        cursor.execute("PRAGMA table_info('%s')" % table)
        cols = [row[1] for row in cursor.fetchall()]
        if 'precio_unitario' not in cols:
            # Add with default 0; SQLite will backfill existing rows
            try:
                cursor.execute(
                    "ALTER TABLE %s ADD COLUMN precio_unitario DECIMAL(10,2) NOT NULL DEFAULT 0" % table
                )
            except Exception:
                pass


def backward(apps, schema_editor):
    # No-op reverse; we don't want to recreate legacy columns
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('bares_snacks', '0007_detallepedido_producto'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
