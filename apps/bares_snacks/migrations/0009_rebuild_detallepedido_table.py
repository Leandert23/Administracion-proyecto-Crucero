from django.db import migrations

REBUILD_SQL = r'''
PRAGMA foreign_keys=OFF;
-- Create new table with the desired schema
CREATE TABLE IF NOT EXISTS bares_snacks_detallepedido_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL DEFAULT 0
);
-- Copy data using existing producto_id only (do not reference non-existent menu_id)
INSERT INTO bares_snacks_detallepedido_new (id, pedido_id, producto_id, cantidad, precio_unitario)
SELECT id,
       pedido_id,
       producto_id,
       cantidad,
       COALESCE(precio_unitario, 0)
FROM bares_snacks_detallepedido;
-- Drop old table and rename
DROP TABLE bares_snacks_detallepedido;
ALTER TABLE bares_snacks_detallepedido_new RENAME TO bares_snacks_detallepedido;
PRAGMA foreign_keys=ON;
'''

REBUILD_SQL_REVERSE = r'''
-- Irreversible: no-op
SELECT 1;
'''

class Migration(migrations.Migration):
    # This migration must not run inside an implicit transaction because
    # SQLite cannot nest transactions and PRAGMA foreign_keys needs to be set
    # outside a transaction to take effect.
    atomic = False
    dependencies = [
        ('bares_snacks', '0008_fix_detallepedido_columns'),
    ]

    operations = [
        migrations.RunSQL(sql=REBUILD_SQL, reverse_sql=REBUILD_SQL_REVERSE),
    ]
