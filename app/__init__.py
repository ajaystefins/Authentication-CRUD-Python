from flask import Flask


# db = get_db()


def create_app():
    print('creating app')
    app = Flask(__name__)
    app.config.update(dict(
        DATABASE="mydb",
        USERNAME="root",
        HOST="localhost",
        PASSWORD="admin",
    ))
    # MySQL configurations
    # app.config['MYSQL_DATABASE_USER'] = 'root'
    # app.config['MYSQL_DATABASE_PASSWORD'] = 'admin'
    # app.config['MYSQL_DATABASE_DB'] = 'mydb'
    # app.config['MYSQL_DATABASE_HOST'] = 'localhost'
    # db.init_app(app)

    from .v1 import v1_blueprint
    app.register_blueprint(v1_blueprint, url_prefix='/api/v1')

    return app
