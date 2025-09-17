from django.db import migrations, connection


def drop_ingredientesreceta(apps, schema_editor):
    with connection.cursor() as cursor:
        # Drop M2M through table if exists
        cursor.execute("PRAGMA foreign_keys=OFF;")
        # IngredientesReceta table name from initial migration is 'bares_snacks_ingredientesreceta'
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bares_snacks_ingredientesreceta'")
        if cursor.fetchone():
            cursor.execute("DROP TABLE bares_snacks_ingredientesreceta")
        cursor.execute("PRAGMA foreign_keys=ON;")


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('bares_snacks', '0013_remove_precio_unitario'),
    ]

    operations = [
        migrations.RunPython(drop_ingredientesreceta, noop),
    ]
    atomic = False
