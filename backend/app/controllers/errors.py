
from flask import jsonify

from ..services.errors import BusinessRuleError, ConflictError, InvalidInputError, NotFoundError


def register_service_errors(app):
    error_statuses = {
        InvalidInputError: 400,
        NotFoundError: 404,
        ConflictError: 409,
        BusinessRuleError: 422,
    }

    def to_response(error):
        return jsonify({"error": str(error)}), error_statuses[type(error)]

    for error_type in error_statuses:
        app.register_error_handler(error_type, to_response)
