
class ServiceError(Exception):
    """Error controlado que la API puede comunicar al cliente."""


class InvalidInputError(ServiceError):
    pass


class NotFoundError(ServiceError):
    pass


class ConflictError(ServiceError):
    pass


class BusinessRuleError(ServiceError):
    pass
