import io

from pypdf import PdfReader

from app.contracts.providers.i_document_text_extractor import IDocumentTextExtractor


class PdfDocumentExtractor(IDocumentTextExtractor):
    def extract_text(self, file_content: bytes) -> str:
        reader = PdfReader(io.BytesIO(file_content))
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            
            if page_text:
                text += page_text + "\n"

        return text.strip()

