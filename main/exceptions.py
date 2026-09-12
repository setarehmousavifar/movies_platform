"""Domain exceptions for service-layer business rules."""


class DomainError(Exception):
    """Base domain/business-rule error."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PermissionDeniedError(DomainError):
    pass


class ValidationDomainError(DomainError):
    pass


class NotFoundError(DomainError):
    pass
