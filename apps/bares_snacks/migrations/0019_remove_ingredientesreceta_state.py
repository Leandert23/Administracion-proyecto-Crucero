from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('bares_snacks', '0018_remove_menu_ingredientes_alter_pedidos_cliente_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(
                    name='IngredientesReceta',
                ),
            ]
        )
    ]
