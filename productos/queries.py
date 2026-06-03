from django.db.models import Count, OuterRef, Subquery, IntegerField, Value, Prefetch, Q
from django.db.models.functions import Coalesce

from .models import Lote, Producto, Unidad, Equipo


def productos_queryset(sucursal_id=None):
    unidades_subquery = (
        Unidad.objects.filter(lote__producto=OuterRef('pk'), status='disponible')
        .values('lote__producto')
        .annotate(total=Count('id'))
    )

    if sucursal_id is not None:
        unidades_subquery = unidades_subquery.filter(lote__sucursal=sucursal_id)

    return (
        Producto.objects.exclude(status='inactivo')
        .select_related('categoria', 'proveedor')
        .prefetch_related(
            Prefetch(
                'equipos',
                queryset=Equipo.objects.filter(activo=True, marca__activo=True).select_related('marca')
            ),
        )
        .annotate(
            cantidad_disponible=Coalesce(
                Subquery(unidades_subquery.values('total'), output_field=IntegerField()),
                Value(0)
            )
        )
    )


def lotes_queryset(sucursal_id=None):
    qs = Lote.objects.exclude(producto__status='inactivo')

    if sucursal_id is not None:
        qs = qs.filter(sucursal=sucursal_id)

    return (
        qs
        .select_related('producto')
        .prefetch_related(
            Prefetch(
                'producto__equipos',
                queryset=Equipo.objects.filter(activo=True, marca__activo=True).select_related('marca')
            ),
        )
        .annotate(cantidad_restante=Count('unidades', filter=Q(unidades__status='disponible')))
    )
