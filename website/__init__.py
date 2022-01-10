from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path,environ
from flask_login import LoginManager
from flask_migrate import Migrate

FILEPATH = "C:/Users/ckron/Desktop/chat-web-app/website/"
DB_NAME = "database.db"
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    uri = environ.get("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    app.config['SECRET_KEY'] = 'mySecretKey'
    app.config['SQLALCHEMY_DATABASE_URI'] = uri or f'sqlite:///{DB_NAME}' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #app = Flask(__name__)
    #app.config['SECRET_KEY'] = 'mySecretKey'
    #app.config['SQLALCHEMY_DATABASE_URI'] =  environ.get("DATABASE_URL") or f'sqlite:///{DB_NAME}' 
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   
    db.init_app(app)
    migrate = Migrate(app, db)

    if not path.isfile(FILEPATH+ DB_NAME):
        db.create_all(app=app)
        print("created")

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app