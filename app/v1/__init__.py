from .resources.auth import auth_ns
from flask import Blueprint
from flask_restx import Api
from .exceptions import ValidationException
import jwt

from .resources.product import product_ns

v1_blueprint = Blueprint('v1_blueprint', __name__)
authorizations = {
    'apikey': {
        'type': 'apiKey',
        # 'scheme': 'bearer',
        'in': 'header',
        'name': 'Authorization'
    }
}
v1_api = Api(v1_blueprint,
             title='Demo API',
             version='1.0',
             description='', authorizations=authorizations)


# from .resources.auth import auth_ns


# from .resources.todo import todo_ns
# from .resources.user import user_ns


@v1_api.errorhandler(ValidationException)
def handle_validation_exception(error):
    return {'message': error.message, 'errors': {error.error_field_name: error.message}}, 400


@v1_api.errorhandler(jwt.ExpiredSignatureError)
def handle_expired_signature_error(error):
    return {'message': 'Token expired'}, 401


@v1_api.errorhandler(jwt.InvalidTokenError)
@v1_api.errorhandler(jwt.DecodeError)
@v1_api.errorhandler(jwt.InvalidIssuerError)
def handle_invalid_token_error(error):
    return {'message': 'Token incorrect, supplied or malformed'}, 401


print('adding namespace')
v1_api.add_namespace(auth_ns)
v1_api.add_namespace(product_ns)
# v1_api.add_namespace(user_ns)
