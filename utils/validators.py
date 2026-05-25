import io
import re

import pdfplumber
from rest_framework import serializers

from .gmail.client import GmailApi


class ValidationError(serializers.ValidationError):
    pass


class FacturaValidator:
    def __init__(self):
        self.gmail = GmailApi()

    def _buscar_pdf_por_factura(self, numero_factura):
        mensajes = self.gmail.find_emails(f"subject:{numero_factura}")
        if not mensajes:
            return None
        msg = self.gmail.get_message(mensajes[0]["id"])
        pdfs = self.gmail.find_pdf_attachments(msg)
        return pdfs[0] if pdfs else None

    def _extraer_texto_de_pdf(self, pdf_data):
        texto_completo = []

        with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    texto_completo.append(text)

        return '\n'.join(texto_completo)

    def _extraer_prefactura(self, text):
        match = re.search(r'ID-(\d+)\|', text)
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
            raise ValidationError(f'No se encontró ningún correo con el número de factura {numero_factura}.')

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
            producto_codigo = item['producto'].codigo_interno
            cantidad = item['cantidad']

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
