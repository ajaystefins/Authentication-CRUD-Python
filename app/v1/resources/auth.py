from flask_restx import Resource, Namespace, fields, marshal
from app.database import get_db
from ..exceptions import ValidationException
from werkzeug.security import generate_password_hash, check_password_hash

from ..utils import generateToken, token_required
import re

auth_ns = Namespace('auth', description='Authentication operations')

register_model = auth_ns.model('Register', {
    'mobile': fields.Integer(required=True),
    'password': fields.String(required=True)
})

# return_token_model = auth_ns.model('ReturnToken', {
#     'access_token': fields.String(required=True),
#     'refresh_token': fields.String(required=True)
# })


@auth_ns.route('/register')
class Register(Resource):
    # 4-16 symbols, can contain A-Z, a-z, 0-9, _ (_ can not be at the begin/end and can not go in a row (__))
    USERNAME_REGEXP = r'^(?![_])(?!.*[_]{2})[a-zA-Z0-9._]+(?<![_])$'

    # Minimum six characters, at least one letter and one number .
    PASSWORD_REGEXP = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$'

    @auth_ns.expect(register_model, validate=True)
    # @auth_ns.marshal_with(User.user_resource_model)
    @auth_ns.response(400, 'Validation failure')
    def post(self):
        # if not re.search(self.USERNAME_REGEXP, auth_ns.payload['username']):
        #     raise ValidationException(error_field_name='username',
        #                               message='4-16 symbols, can contain A-Z, a-z, 0-9, _ \
        #                               (_ can not be at the begin/end and can not go in a row (__))')

        if not re.search(self.PASSWORD_REGEXP, auth_ns.payload['password']):
            raise ValidationException(error_field_name='password',
                                      message='Password must contain minimum six characters, at least one letter and one number')

        conn = get_db()
        cursor = conn.cursor()
        sql = "SELECT user_id FROM users WHERE user_mobile= %s"
        data = auth_ns.payload['mobile']
        cursor.execute(sql, (data,))
        rows = cursor.fetchall()
        if rows:  # user already present
            raise ValidationException(
                error_field_name='mobile', message='This mobile number already exists')
        _hashed_password = generate_password_hash(auth_ns.payload['password'])
        sql = "INSERT INTO users(user_mobile,  user_password) VALUES(%s,  %s)"
        data = (auth_ns.payload['mobile'], _hashed_password,)
        cursor.execute(sql, data)
        conn.commit()
        access_token = generateToken(cursor.lastrowid)

        return {'success': True, 'access_token': access_token}


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(register_model, validate=True)
    # @auth_ns.response(200, 'Success', return_token_model)
    @auth_ns.response(401, 'Incorrect username or password')
    def post(self):
        # """
        # Look implementation notess
        # This API implemented JWT. Token's payload contain:
        # 'uid' (user id),
        # 'exp' (expiration date of the token),
        # 'iat' (the time the token is generated)
        # """

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT user_id,user_password FROM users WHERE user_mobile= %s"
        data = auth_ns.payload['mobile']
        cursor.execute(sql, (data,))
        user = cursor.fetchone()
        if not user:
            auth_ns.abort(401, 'Incorrect username or password')
        if check_password_hash(user['user_password'], auth_ns.payload['password']):
            access_token = generateToken(user['user_id'])
            return {'success': True, 'access_token': access_token}, 200
        else:
            auth_ns.abort(401, 'Incorrect username or password')


# @auth_ns.route('/users')
# class Users(Resource):
#     @token_required
#     # @auth_ns.expect(register_model)
#     # @auth_ns.response(200, 'Success', return_token_model)
#     @auth_ns.response(401, 'Incorrect username or password')
#     def get(self, current_user):
#         return current_user

# from ..utils import token_required
#
#
# # This resource only for test
# @auth_ns.route('/protected')
# class Protected(Resource):
#     @token_required
#     def get(self, current_user):
#         return {'i am': 'protected', 'uid': current_user.id}
