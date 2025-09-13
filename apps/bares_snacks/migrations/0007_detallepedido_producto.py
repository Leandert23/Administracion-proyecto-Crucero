from django.db import migrations, connection


def safe_apply(apps, schema_editor):
    """Idempotente: sólo agrega columnas que falten y deja existente sin duplicar."""
    table = 'bares_snacks_detallepedido'
    with connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info('{table}')")
        cols = [r[1] for r in cursor.fetchall()]

        # Agregar producto_id si no está (antes era menu_id)
        if 'producto_id' not in cols:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN producto_id INTEGER REFERENCES bares_snacks_productobar(id)")
            except Exception:
                pass

        # Agregar precio_unitario si falta
        cursor.execute(f"PRAGMA table_info('{table}')")
        cols = [r[1] for r in cursor.fetchall()]
        if 'precio_unitario' not in cols:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN precio_unitario DECIMAL(10,2) NOT NULL DEFAULT 0")
            except Exception:
                pass

        # Intentar mapear valores antiguos si sólo existe menu_id y no producto_id (caso raro post-add)
        cursor.execute(f"PRAGMA table_info('{table}')")
        cols = [r[1] for r in cursor.fetchall()]
        if 'menu_id' in cols and 'producto_id' in cols:
            # No se elimina menu_id aquí por compatibilidad (SQLite < 3.35 no soporta DROP COLUMN)
            pass


class Migration(migrations.Migration):
    dependencies = [
        ('bares_snacks', '0006_remove_pedidos_instalacion_consumo'),
    ]

    operations = [
        migrations.RunPython(safe_apply, migrations.RunPython.noop),
    ]