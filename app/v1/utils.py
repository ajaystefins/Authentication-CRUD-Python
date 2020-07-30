from datetime import datetime, timedelta

import jwt
from config import Config
from flask import request, current_app, abort
from ..database import get_db


def token_required(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        current_user = None
        if auth_header:
            try:
                # access_token = auth_header.split(' ')[1]
                access_token = auth_header
                try:
                    print(Config.SECRET_KEY)
                    token = jwt.decode(access_token, Config.SECRET_KEY, options={
                                       'verify_exp': False})
                    print(token)
                    conn = get_db()
                    cursor = conn.cursor(dictionary=True)
                    sql = "SELECT user_id,user_mobile FROM users WHERE user_id= %s"
                    data = token['uid']
                    print(data)
                    cursor.execute(sql, (data,))
                    current_user = cursor.fetchone()
                    print(data)
                except jwt.ExpiredSignatureError as e:
                    # raise e
                    pass
                except (jwt.DecodeError, jwt.InvalidTokenError) as e:
                    raise e
                except Exception as e:
                    abort(401, 'Unknown token error ' + e.__str__())

            except IndexError:
                raise jwt.InvalidTokenError
        else:
            abort(403, 'Token required')
        return f(*args, **kwargs, current_user=current_user)

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


def generateToken(userId):
    _access_token = jwt.encode({'uid': userId,
                                'exp': datetime.utcnow() + timedelta(minutes=15),
                                'iat': datetime.utcnow()},
                               Config.SECRET_KEY).decode('utf-8')
    return _access_token
