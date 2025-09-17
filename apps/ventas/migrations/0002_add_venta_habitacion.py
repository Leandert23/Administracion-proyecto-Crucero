# Generated manually for adding VentaHabitacion model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('creador_embarcaciones', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ventas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VentaHabitacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_cliente', models.CharField(max_length=100, verbose_name='Nombre')),
                ('apellido_cliente', models.CharField(max_length=100, verbose_name='Apellido')),
                ('numero_pasaporte', models.CharField(max_length=50, verbose_name='Número de Pasaporte')),
                ('precio_venta', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio de Venta')),
                ('fecha_venta', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Venta')),
                ('fecha_checkin', models.DateField(blank=True, null=True, verbose_name='Fecha de Check-in')),
                ('fecha_checkout', models.DateField(blank=True, null=True, verbose_name='Fecha de Check-out')),
                ('estado', models.CharField(choices=[('reservada', 'Reservada'), ('ocupada', 'Ocupada'), ('completada', 'Completada'), ('cancelada', 'Cancelada')], default='reservada', max_length=20, verbose_name='Estado')),
                ('notas', models.TextField(blank=True, verbose_name='Notas adicionales')),
                ('embarcacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ventas_habitaciones', to='creador_embarcaciones.embarcacion')),
                ('habitacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ventas_habitacion', to='creador_embarcaciones.habitaciones')),
                ('vendedor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Vendedor')),
            ],
            options={
                'verbose_name': 'Venta de Habitación',
                'verbose_name_plural': 'Ventas de Habitaciones',
                'ordering': ['-fecha_venta'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='ventahabitacion',
            unique_together={('habitacion', 'fecha_checkin')},
        ),
    ]
