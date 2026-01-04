from typing import Protocol


class IDocumentTextExtractor(Protocol):
    """
    Interface for extracting text content from various document formats.
    """

    def extract_text(self, file_content: bytes) -> str:
        """
        Extracts plain text from the provided file content.

        Args:
            file_content (bytes): The raw binary content of the file.

        Returns:
            str: The extracted text.
        """
        ...

