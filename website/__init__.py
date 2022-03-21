from flask import Flask,Blueprint,blueprints
from flask_sqlalchemy import SQLAlchemy
from os import path,environ
from flask_login import LoginManager
from flask_migrate import Migrate

FILEPATH = "website/"
DB_NAME = "database.db"

db = SQLAlchemy()

def create_app():
    db_online = False
    app = Flask(__name__)
    uri = environ.get("DATABASE_URL")

    if uri and uri.startswith("postgres://"):
        db_online = True
        uri = uri.replace("postgres://", "postgresql://", 1)

    app.config['SECRET_KEY'] = 'mySecretKey'
    app.config['SQLALCHEMY_DATABASE_URI'] = uri or f'sqlite:///{DB_NAME}' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #app = Flask(__name__)
    #app.config['SECRET_KEY'] = 'mySecretKey'
    #app.config['SQLALCHEMY_DATABASE_URI'] =  HEROKU_URI
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   
    db.init_app(app)
    #migrate = Migrate(app=app,db=db)
    
    if (path.isfile(FILEPATH+DB_NAME) is not True) and (db_online == False):
        db.create_all(app=app)
        print("created")
        
    from . import views,auth
    app.register_blueprint(views.views, url_prefix='/')
    app.register_blueprint(auth.auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app,db_online