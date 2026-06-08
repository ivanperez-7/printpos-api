from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movimiento', '0015_movimientoitem_cambio_anticipado_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='detallesalida',
            name='subtipo',
            field=models.CharField(
                choices=[('venta', 'Venta'), ('renta', 'Renta')],
                default='renta',
                max_length=10,
            ),
            # Backfill: todas las salidas históricas son renta. El default no se
            # conserva en el estado del modelo (subtipo es requerido en adelante).
            preserve_default=False,
        ),
    ]
