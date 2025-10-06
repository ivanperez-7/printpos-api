from django.db.models import Case, CharField, F, Value, When
from django.db.models.functions import Cast, Concat
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import *


@api_view()
@permission_classes([IsAuthenticated])
def get_all_movimientos_caja(request):
    qs_ventas_pagos = VentaPago.objects.annotate(
        descripcion=Concat(
            Case(When(monto__gt=0.0, then=Value('Pago')), default=Value('Devolución')),
            Value(' de venta con folio '),
            Cast(F('venta_id'), CharField())
        )
    )
    all_movimientos = qs_ventas_pagos.union(Caja.objects.all()).order_by('-fecha_hora')
    data = all_movimientos.values('fecha_hora', 'monto', 'descripcion', 'metodo_pago__metodo', 'usuario__username')

    return Response(data=data, status=200)
