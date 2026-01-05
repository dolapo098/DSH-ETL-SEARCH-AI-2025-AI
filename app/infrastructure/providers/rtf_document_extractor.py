from striprtf.striprtf import rtf_to_text

from app.contracts.providers.i_document_text_extractor import IDocumentTextExtractor


class RtfDocumentExtractor(IDocumentTextExtractor):

    def extract_text(self, file_content: bytes) -> str:

        try:
            rtf_string = file_content.decode('cp1252', errors='ignore')
            return rtf_to_text(rtf_string, errors='ignore').strip()
        except Exception:
            return ""

