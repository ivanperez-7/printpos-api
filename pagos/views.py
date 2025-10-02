from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import *
from .pdf import generar_corte_pdf
from .serializers import CajaSerializer


class CajaViewSet(ModelViewSet):
    queryset = Caja.objects.all()
    serializer_class = CajaSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_all_movimientos_caja(request):
    qs_ventas_pagos = VentaPago.objects.con_descripcion().all()
    qs_caja = Caja.objects.all()

    if (
        (f_inicio := request.data.get('fecha_inicio'))
        and (f_fin := request.data.get('fecha_fin'))
    ):
        qs_ventas_pagos = qs_ventas_pagos.filter(fecha_hora__date__gte=f_inicio, fecha_hora__date__lte=f_fin)
        qs_caja = qs_caja.filter(fecha_hora__date__gte=f_inicio, fecha_hora__date__lte=f_fin)

    all_movimientos = qs_ventas_pagos.union(qs_caja).order_by('-fecha_hora')
    data = all_movimientos.values('fecha_hora', 'monto', 'descripcion', 'metodo_pago__metodo', 'usuario__username')
    return Response(data=data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report_pdf(request):
    if not 'fecha_inicio' in request.data or not 'fecha_fin' in request.data:
        return Response(data={"error": "Se requieren las fechas de inicio y fin"}, status=500)
    
    f_inicio = request.data.get('fecha_inicio')
    f_fin = request.data.get('fecha_fin')

    qs_ventas_pagos = VentaPago.objects.con_descripcion().filter(
        fecha_hora__date__gte=f_inicio, fecha_hora__date__lte=f_fin
    )
    qs_caja = Caja.objects.filter(fecha_hora__date__gte=f_inicio, fecha_hora__date__lte=f_fin)

    all_movimientos = qs_ventas_pagos.union(qs_caja).order_by('-fecha_hora')
    pdf_buffer = generar_corte_pdf(
        all_movimientos,
        responsable=request.user.username
    )

    response = Response(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_corte.pdf"'
    response.content = pdf_buffer.getvalue()
    return response
