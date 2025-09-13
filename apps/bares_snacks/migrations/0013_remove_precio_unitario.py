from django.db import migrations, connection


def drop_precio_unitario(apps, schema_editor):
    table = 'bares_snacks_detallepedido'
    with connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info('{table}')")
        cols = [c[1] for c in cursor.fetchall()]
        if 'precio_unitario' not in cols:
            return  # nothing to do
        # Rebuild table without precio_unitario
        new_table = table + '_new'
        cursor.execute("PRAGMA foreign_keys=OFF;")
        cursor.execute(f"DROP TABLE IF EXISTS {new_table}")
        cursor.execute(
            f"""
            CREATE TABLE {new_table} (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              pedido_id INTEGER NOT NULL REFERENCES bares_snacks_pedidos(id) DEFERRABLE INITIALLY DEFERRED,
              producto_id INTEGER NOT NULL REFERENCES bares_snacks_productobar(id) DEFERRABLE INITIALLY DEFERRED,
              cantidad INTEGER NOT NULL
            )
            """
        )
        # Copy data (skip precio_unitario)
        cursor.execute(
            f"INSERT INTO {new_table} (id, pedido_id, producto_id, cantidad)\n"
            f"SELECT id, pedido_id, producto_id, cantidad FROM {table}"
        )
        cursor.execute(f"DROP TABLE {table}")
        cursor.execute(f"ALTER TABLE {new_table} RENAME TO {table}")
        cursor.execute("PRAGMA foreign_keys=ON;")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('bares_snacks', '0012_rebuild_detallepedido_final'),
    ]

    operations = [
        migrations.RunPython(drop_precio_unitario, noop),
    ]
    atomic = False
