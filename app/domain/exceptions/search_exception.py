from app.domain.exceptions.app_error_code import AppErrorCode
from app.domain.exceptions.api_exception import ApiException


class SearchException(ApiException):
    """
    Base class for all search-related exceptions.
    """

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code, AppErrorCode.SEARCH_ERROR)


class VectorStoreException(SearchException):
    """
    Raised when an operation in the vector store fails.
    """

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code)
        
        self.app_code = AppErrorCode.VECTOR_STORE_ERROR


class EmbeddingGenerationException(SearchException):
    """
    Raised when text embedding generation fails.
    """

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code)
        
        self.app_code = AppErrorCode.EMBEDDING_ERROR


class InvalidSearchQueryException(SearchException):
    """
    Raised when a search query is malformed or invalid.
    """

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code)
        
        self.app_code = AppErrorCode.VALIDATION_ERROR
