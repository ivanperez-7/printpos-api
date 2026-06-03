from django.db import migrations


def backfill_sucursal(apps, schema_editor):
    RegistroActividad = apps.get_model('system', 'RegistroActividad')
    RegistroActividad.objects.filter(sucursal__isnull=True).update(sucursal_id=1)


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_registroactividad_sucursal'),
    ]

    operations = [
        migrations.RunPython(backfill_sucursal),
    ]
