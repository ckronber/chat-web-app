from flask import Flask,Blueprint,blueprints
from flask_sqlalchemy import SQLAlchemy
from os import path,environ
from flask_login import LoginManager
from flask_migrate import Migrate
import json

FILEPATH = "chatApp/website/"
DB_NAME = "database.db"
HEROKU_URI = "postgres://wssjwvjerqtxlr:598fd557ca3fc4fa1c6e8de14bb1ca6b4cdd94ee72f4737394aa9a268077aa08@ec2-54-161-238-249.compute-1.amazonaws.com:5432/dfj6jr90dri7lg"

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    #uri = environ.get("DATABASE_URL")
    #if uri and uri.startswith("postgres://"):
    #    uri = uri.replace("postgres://", "postgresql://", 1)

    app.config['SECRET_KEY'] = 'mySecretKey'
    #app.config['SQLALCHEMY_DATABASE_URI'] = uri or f'sqlite:///{DB_NAME}' 
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #app = Flask(__name__)
    #app.config['SECRET_KEY'] = 'mySecretKey'
    app.config['SQLALCHEMY_DATABASE_URI'] =  HEROKU_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   
    db.init_app(app)
    migrate = Migrate(app=app,db=db)

    if path.isfile(FILEPATH+DB_NAME) is not True:
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

    return app