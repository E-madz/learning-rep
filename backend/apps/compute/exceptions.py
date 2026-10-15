"""Domain exceptions: the service layer raises these, the API layer maps them to HTTP codes."""


class DomainError(Exception):
    pass


class QuotaExceeded(DomainError):
    pass


class InvalidStateTransition(DomainError):
    pass


class VirtualMachineNotFound(DomainError):
    pass


class NameAlreadyExists(DomainError):
    pass
