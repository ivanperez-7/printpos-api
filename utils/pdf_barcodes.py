import io

from reportlab.graphics.barcode.code128 import Code128
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


COLS = 3
ROWS = 8
LABELS_PER_PAGE = COLS * ROWS

MARGIN_LEFT = 0.15 * inch
MARGIN_TOP = 0.2 * inch

PAGE_W, PAGE_H = letter
LABEL_W = PAGE_W / COLS
LABEL_H = PAGE_H / ROWS


def generate_lot_labels_pdf(lots):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    for idx, lot in enumerate(lots):
        pos = idx % LABELS_PER_PAGE
        if pos == 0 and idx > 0:
            c.showPage()

        col = pos % COLS
        row = pos // COLS
        x0 = col * LABEL_W + MARGIN_LEFT
        y0 = PAGE_H - (row + 1) * LABEL_H + MARGIN_TOP

        c.rect(x0 - 0.05 * inch, y0 - 0.05 * inch,
               LABEL_W - 0.2 * inch, LABEL_H - 0.25 * inch)

        bc = Code128(value=lot.codigo_lote, barHeight=24, barWidth=0.6)
        bc.drawOn(c, x0, y0 + 34)

        c.setFont('Helvetica', 6)
        prod_text = f'{lot.producto.codigo_interno} - {lot.producto.descripcion}'
        max_chars = int((LABEL_W - 0.3 * inch) / 2.5)
        if len(prod_text) > max_chars:
            prod_text = prod_text[:max_chars - 3] + '...'
        c.drawString(x0, y0 + 26, prod_text)

        c.setFont('Courier', 8)
        c.drawString(x0, y0 + 16, lot.codigo_lote)

        c.setFont('Helvetica', 6.5)
        c.drawString(x0, y0 + 6, f'Cant: {lot.cantidad_inicial}  |  {lot.fecha_entrada.strftime("%d/%m/%Y")}')

    c.save()
    return buf.getvalue()
