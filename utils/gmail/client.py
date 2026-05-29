import base64

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .auth import authenticate


class GmailApi:
    def __init__(self):
        creds = authenticate()
        self.service = build("gmail", "v1", credentials=creds)

    def find_emails(self, query, max_results=50):
        request = (
            self.service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
        )
        result = self._execute_request(request)
        return result.get("messages", [])

    def get_message(self, message_id):
        request = self.service.users().messages().get(
            userId="me", id=message_id, format="full"
        )
        return self._execute_request(request)

    def get_attachment_data(self, message_id, attachment_id):
        request = self.service.users().messages().attachments().get(
            userId="me", messageId=message_id, id=attachment_id
        )
        result = self._execute_request(request)
        data = result["data"].replace("-", "+").replace("_", "/")
        return base64.b64decode(data)

    def _is_pdf_attachment(self, part):
        if part["mimeType"] == "application/pdf":
            return True
        if part["mimeType"] == "application/octet-stream" and (
            part.get("filename", "").lower().endswith(".pdf")
        ):
            return True
        return False

    def find_pdf_attachments(self, message):
        pdfs = []
        parts = message["payload"].get("parts", [])
        
        for part in parts:
            if self._is_pdf_attachment(part):
                body = part.get("body", {})
                if "attachmentId" in body:
                    data = self.get_attachment_data(
                        message["id"], body["attachmentId"]
                    )
                    pdfs.append(data)
                elif "data" in body:
                    raw = body["data"].replace("-", "+").replace("_", "/")
                    pdfs.append(base64.b64decode(raw))
        return pdfs

    @staticmethod
    def _execute_request(request):
        try:
            return request.execute()
        except HttpError as e:
            raise RuntimeError(e)
