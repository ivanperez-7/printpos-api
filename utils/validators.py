import io
import re
from datetime import datetime, timedelta

import pdfplumber
from rest_framework.serializers import ValidationError

from .gmail.client import GmailApi


class FacturaValidator:
    def __init__(self):
        self.gmail = GmailApi()

    def _buscar_pdf_por_factura(self, numero_factura):
        """ Busca en Gmail un correo con un PDF adjunto que contenga el número de prefactura especificado."""
        hoy = datetime.now()
        inicio_busqueda = (hoy - timedelta(days=90)).strftime("%Y/%m/%d")
        fin_busqueda = hoy.strftime("%Y/%m/%d")

        query = (
            f"has:attachment filename:pdf from:konicaminolta "
            f"subject:Prefactura after:{inicio_busqueda} before:{fin_busqueda}"
        )
        mensajes = self.gmail.find_emails(query)

        if not mensajes:
            return None
        for msg_info in mensajes:
            msg = self.gmail.get_message(msg_info["id"])
            pdfs = self.gmail.find_pdf_attachments(msg)

            for pdf_data in pdfs:
                texto = self._extraer_texto_de_pdf(pdf_data)
                if re.search(rf'ID-{numero_factura}', texto):
                    return pdf_data
        return None

    def _extraer_texto_de_pdf(self, pdf_data):
        texto_completo = []

        with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    texto_completo.append(text)

        return '\n'.join(texto_completo)

    def _extraer_prefactura(self, text):
        match = re.search(r'ID-(\d+)', text)
        return match.group(1) if match else None

    def _normalizar_texto(self, texto):
        if texto is None:
            return ''
        texto = str(texto).strip().lower()
        texto = re.sub(r'\s+', ' ', texto)
        return texto

    def _buscar_producto_en_texto(self, producto_codigo, cantidad, text):
        producto_normalizado = self._normalizar_texto(producto_codigo)
        text_normalizado = self._normalizar_texto(text)

        if producto_normalizado not in text_normalizado:
            return False

        lines = text.split('\n')
        for i, line in enumerate(lines):
            if producto_normalizado in self._normalizar_texto(line):
                for j in range(i, min(i + 5, len(lines))):
                    qty_match = re.search(r'(\d+)\s*\$', lines[j])
                    if qty_match and int(qty_match.group(1)) == cantidad:
                        return True
        return False

    def validar(self, numero_factura, items):
        pdf_data = self._buscar_pdf_por_factura(numero_factura)

        if not pdf_data:
            raise ValidationError(f'No se encontró ningún correo con el número de prefactura {numero_factura}.')

        texto = self._extraer_texto_de_pdf(pdf_data)

        if not texto:
            raise ValidationError('No se pudo extraer texto de la prefactura.')

        prefactura = self._extraer_prefactura(texto)
        if prefactura and prefactura != numero_factura:
            raise ValidationError(
                f'Número de prefactura discrepante: PDF={prefactura}, solicitud={numero_factura}.'
            )

        errores = []

        for item in items:
            producto_codigo = item.producto.codigo_interno
            cantidad = item.cantidad

            if not self._buscar_producto_en_texto(producto_codigo, cantidad, texto):
                errores.append(
                    f'Producto {producto_codigo} con cantidad {cantidad} no encontrado en la prefactura.'
                )

        if errores:
            raise ValidationError('Información discrepante: ' + '; '.join(errores))

        return True


def validar_factura_entrada(numero_factura, items):
    validator = FacturaValidator()
    return validator.validar(numero_factura, items)
