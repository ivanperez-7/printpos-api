import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0007_fill_registroactividad_sucursal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registroactividad',
            name='sucursal',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='actividades',
                to='organizacion.sucursal',
            ),
        ),
    ]
