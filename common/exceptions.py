class AppException(Exception):
    """Base class for all application-level exceptions."""

    status_code: int = 500
    code: str = "application_error"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        status_code: int | None = None,
        code: str | None = None,
        details: dict | None = None,
    ) -> None:
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        self.code = code or self.code
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppException):
    status_code = 404
    code = "not_found"
    message = "Resource not found."


class ConflictError(AppException):
    status_code = 409
    code = "conflict"
    message = "Resource already exists."


class UnauthorizedError(AppException):
    status_code = 401
    code = "unauthorized"
    message = "Authentication required."


class ForbiddenError(AppException):
    status_code = 403
    code = "forbidden"
    message = "You do not have permission to perform this action."


class BadRequestError(AppException):
    status_code = 400
    code = "bad_request"
    message = "Invalid request."


class ServiceUnavailableError(AppException):
    status_code = 503
    code = "service_unavailable"
    message = "A required service is temporarily unavailable."
