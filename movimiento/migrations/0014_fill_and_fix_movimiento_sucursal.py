from django.db import migrations, models


def fill_sucursal(apps, schema_editor):
    Movimiento = apps.get_model('movimiento', 'Movimiento')
    Sucursal = apps.get_model('organizacion', 'Sucursal')
    default, _ = Sucursal.objects.get_or_create(pk=1, defaults={'nombre': 'Default'})
    Movimiento.objects.filter(sucursal__isnull=True).update(sucursal=default)


class Migration(migrations.Migration):

    dependencies = [
        ('movimiento', '0013_movimiento_sucursal'),
    ]

    operations = [
        migrations.RunPython(fill_sucursal, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='movimiento',
            name='sucursal',
            field=models.ForeignKey(
                'organizacion.Sucursal',
                on_delete=models.deletion.PROTECT,
                related_name='movimientos',
            ),
        ),
    ]
