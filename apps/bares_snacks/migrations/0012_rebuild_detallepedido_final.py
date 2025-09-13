from django.db import migrations, connection


def rebuild_detallepedido(apps, schema_editor):
    table = 'bares_snacks_detallepedido'
    new_table = table + '_new'
    with connection.cursor() as cursor:
        # Detect existing columns
        cursor.execute(f"PRAGMA table_info('{table}')")
        cols_info = cursor.fetchall()
        existing_cols = [c[1] for c in cols_info]
        if not existing_cols:
            # Table missing? Just create fresh
            cursor.execute(
                f"""
                CREATE TABLE {table} (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  pedido_id INTEGER NOT NULL REFERENCES bares_snacks_pedidos(id) DEFERRABLE INITIALLY DEFERRED,
                  producto_id INTEGER NOT NULL REFERENCES bares_snacks_productobar(id) DEFERRABLE INITIALLY DEFERRED,
                  cantidad INTEGER NOT NULL,
                  precio_unitario DECIMAL(10,2) NOT NULL DEFAULT 0
                )
                """
            )
            return

        # Build new table
        cursor.execute("PRAGMA foreign_keys=OFF;")
        cursor.execute(f"DROP TABLE IF EXISTS {new_table}")
        cursor.execute(
            f"""
            CREATE TABLE {new_table} (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              pedido_id INTEGER NOT NULL REFERENCES bares_snacks_pedidos(id) DEFERRABLE INITIALLY DEFERRED,
              producto_id INTEGER NOT NULL REFERENCES bares_snacks_productobar(id) DEFERRABLE INITIALLY DEFERRED,
              cantidad INTEGER NOT NULL,
              precio_unitario DECIMAL(10,2) NOT NULL DEFAULT 0
            )
            """
        )

        has_precio = 'precio_unitario' in existing_cols
        source_producto = 'producto_id' if 'producto_id' in existing_cols else None
        if not source_producto:
                # Nothing to migrate, just rename new
                cursor.execute(f"DROP TABLE {table}")
                cursor.execute(f"ALTER TABLE {new_table} RENAME TO {table}")
                cursor.execute("PRAGMA foreign_keys=ON;")
                return

        # Copy rows
        if has_precio:
            insert_sql = f"""
                INSERT INTO {new_table} (id, pedido_id, producto_id, cantidad, precio_unitario)
                SELECT id, pedido_id, {source_producto} as producto_id, cantidad,
                       COALESCE(precio_unitario, (
                           SELECT COALESCE(pb.precio_vta,0) FROM bares_snacks_productobar pb WHERE pb.id = {source_producto}
                       ), 0)
                FROM {table}
            """
        else:
            insert_sql = f"""
                INSERT INTO {new_table} (id, pedido_id, producto_id, cantidad, precio_unitario)
                SELECT id, pedido_id, {source_producto} as producto_id, cantidad,
                       COALESCE((
                           SELECT COALESCE(pb.precio_vta,0) FROM bares_snacks_productobar pb WHERE pb.id = {source_producto}
                       ),0)
                FROM {table}
            """
        cursor.execute(insert_sql)

        # Replace old table
        cursor.execute(f"DROP TABLE {table}")
        cursor.execute(f"ALTER TABLE {new_table} RENAME TO {table}")
        cursor.execute("PRAGMA foreign_keys=ON;")


class Migration(migrations.Migration):
    dependencies = [
        ('bares_snacks', '0011_force_precio_unitario'),
    ]

    operations = [
        migrations.RunPython(rebuild_detallepedido, migrations.RunPython.noop),
    ]
    # Needed for SQLite PRAGMA and table rebuild operations
    atomic = False
