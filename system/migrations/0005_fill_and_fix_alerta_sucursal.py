from django.db import migrations, models


def fill_sucursal(apps, schema_editor):
    AlertaInventario = apps.get_model('system', 'AlertaInventario')
    Sucursal = apps.get_model('organizacion', 'Sucursal')
    default, _ = Sucursal.objects.get_or_create(pk=1, defaults={'nombre': 'Default'})
    AlertaInventario.objects.filter(sucursal__isnull=True).update(sucursal=default)


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0004_alertainventario_sucursal'),
    ]

    operations = [
        migrations.RunPython(fill_sucursal, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='alertainventario',
            name='sucursal',
            field=models.ForeignKey(
                'organizacion.Sucursal',
                on_delete=models.deletion.PROTECT,
                related_name='alertas',
            ),
        ),
    ]
