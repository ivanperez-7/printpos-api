""" Provee métodos para generar diversos PDF en bytes. """
import io
from collections import defaultdict
from datetime import datetime

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def generar_corte_pdf(caja_pagos_union, responsable: str):
    """ Genera un PDF con el resumen de movimientos de caja y pagos de ventas.
        Recibe una QuerySet que es la unión de los modelos Caja y VentaPago. 
        Devuelve un buffer de bytes con el PDF generado. """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=(80 * mm, 297 * mm),
        topMargin=0, bottomMargin=0, leftMargin=0, rightMargin=0
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Left', fontName='Helvetica', fontSize=9, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Foot', fontName='Helvetica', fontSize=11, alignment=TA_LEFT))

    datos = list(caja_pagos_union.values('metodo_pago__metodo', 'monto'))

    ingresos = defaultdict(float)
    egresos = defaultdict(float)
    for row in datos:
        metodo = row['metodo_pago__metodo']
        monto = float(row['monto'] or 0)
        if monto >= 0:
            ingresos[metodo] += monto
        else:
            egresos[metodo] += abs(monto)

    metodos = sorted(set(ingresos) | set(egresos))
    prefer_order = ['Efectivo', 'Tarjeta de crédito', 'Tarjeta de débito', 'Transferencia']
    ordered_metodos = [m for m in prefer_order if m in metodos] + [m for m in metodos if m not in prefer_order]

    total_ingresos = sum(ingresos.values())
    total_egresos = sum(egresos.values())
    esperado = total_ingresos - total_egresos

    elements = [
        Paragraph('Resumen de movimientos de caja', styles['Heading1']),
        Spacer(1, 6),
        Paragraph(f'Realizado por: {responsable}', styles['Left']),
        Paragraph(f'Fecha y hora: {datetime.now():%d/%m/%Y %H:%M}', styles['Left']),
        Spacer(1, 6),
        Paragraph('Resumen de ingresos', styles['Heading3']),
    ]

    for m in ordered_metodos:
        elements.append(Paragraph(f'{m}: ${ingresos[m]:.2f}', styles['Left']))

    elements += [
        Spacer(1, 6),
        Paragraph('Resumen de egresos', styles['Heading3']),
    ]
    for m in ordered_metodos:
        elements.append(Paragraph(f'{m}: ${egresos[m]:.2f}', styles['Left']))

    elements += [
        Spacer(1, 6),
        Paragraph('Esperado por método (ingresos - egresos)', styles['Heading3']),
    ]
    for m in ordered_metodos:
        val = ingresos[m] - egresos[m]
        elements.append(Paragraph(f'{m}: ${val:.2f}', styles['Left']))

    elements += [
        Spacer(1, 20),
        Paragraph(f'<b>Total de ingresos</b>: ${total_ingresos:.2f}', styles['Foot']),
        Paragraph(f'<b>Total de egresos</b>: ${total_egresos:.2f}', styles['Foot']),
        Paragraph(f'<b>Esperado en caja</b>: ${esperado:.2f}', styles['Foot']),
    ]

    doc.build(elements)
    return buffer
