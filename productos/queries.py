from django.db.models import Count, OuterRef, Subquery, IntegerField, Value, Prefetch, Q
from django.db.models.functions import Coalesce

from .models import Lote, Producto, Unidad, Equipo


def productos_queryset():
    unidades_subquery = (
        Unidad.objects.filter(lote__producto=OuterRef('pk'), status='disponible')
        .values('lote__producto')
        .annotate(total=Count('id'))
    )

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


def lotes_queryset():
    return (
        Lote.objects.exclude(producto__status='inactivo')
        .select_related('producto')
        .prefetch_related(
            Prefetch(
                'producto__equipos',
                queryset=Equipo.objects.filter(activo=True, marca__activo=True).select_related('marca')
            ),
        )
        .annotate(cantidad_restante=Count('unidades', filter=Q(unidades__status='disponible')))
    )
