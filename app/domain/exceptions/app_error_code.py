from enum import IntEnum


class AppErrorCode(IntEnum):
    """
    Error codes for application-specific exceptions.
    """

    ValidationFailed = 100
    SEARCH_ERROR = 200
    VECTOR_STORE_ERROR = 201
    EMBEDDING_ERROR = 202
    VALIDATION_ERROR = 203
    InternalServerError = 500
    UnAuthorized = 401
