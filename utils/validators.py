import imaplib
import email
import io
import os
import re

import pdfplumber
from rest_framework import serializers


class ValidationError(serializers.ValidationError):
    pass


class FacturaValidator:
    def __init__(self):
        self.email_host = os.getenv('EMAIL_HOST')
        self.email_port = os.getenv('EMAIL_PORT')
        self.email_username = os.getenv('EMAIL_USERNAME')
        self.email_password = os.getenv('EMAIL_PASSWORD')

    def _connect(self):
        mail = imaplib.IMAP4_SSL(str(self.email_host), int(self.email_port))
        mail.login(str(self.email_username), str(self.email_password))
        mail.select('INBOX')
        return mail

    def _buscar_correo_por_factura(self, numero_factura):
        mail = self._connect()
        search_criteria = f'SUBJECT "{numero_factura}"'

        try:
            status, messages = mail.search(None, search_criteria)
            if status != 'OK':
                mail.logout()
                return None

            email_ids = messages[0].split()
            if not email_ids:
                mail.logout()
                return None

            latest_email_id = email_ids[-1]
            status, msg_data = mail.fetch(latest_email_id, '(RFC822)')

            if status != 'OK':
                mail.logout()
                return None

            msg = email.message_from_bytes(msg_data[0][1])
            mail.logout()
            return msg
        except Exception as e:
            try:
                mail.logout()
            except:
                pass
            raise ValidationError(f'Error al buscar correo: {str(e)}')

    def _extraer_pdf_de_correo(self, msg):
        for part in msg.walk():
            if part.get_content_type() == 'application/pdf':
                return part.get_payload(decode=True)
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
        if not all([self.email_host, self.email_port, self.email_username, self.email_password]):
            raise ValidationError('Credenciales de correo no configuradas en el entorno.')

        msg = self._buscar_correo_por_factura(numero_factura)

        if not msg:
            raise ValidationError(f'No se encontró ningún correo con el número de factura {numero_factura}.')

        pdf_data = self._extraer_pdf_de_correo(msg)

        if not pdf_data:
            raise ValidationError('No se encontró ningún PDF adjunto en el correo.')

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
