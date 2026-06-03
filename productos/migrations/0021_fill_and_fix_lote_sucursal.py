from django.db import migrations, models


def fill_sucursal(apps, schema_editor):
    Lote = apps.get_model('productos', 'Lote')
    Sucursal = apps.get_model('organizacion', 'Sucursal')
    default, _ = Sucursal.objects.get_or_create(pk=1, defaults={'nombre': 'Default'})
    Lote.objects.filter(sucursal__isnull=True).update(sucursal=default)


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0020_lote_sucursal'),
    ]

    operations = [
        migrations.RunPython(fill_sucursal, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='lote',
            name='sucursal',
            field=models.ForeignKey(
                'organizacion.Sucursal',
                on_delete=models.deletion.PROTECT,
                related_name='lotes',
            ),
        ),
    ]
