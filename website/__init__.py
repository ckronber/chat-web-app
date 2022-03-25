from flask import Flask,Blueprint,blueprints
from flask_sqlalchemy import SQLAlchemy
from os import path,environ,remove
from flask_login import LoginManager
from flask_migrate import Migrate

FILEPATH = "website/"
DB_NAME = "database.db"

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    uri = environ.get("DATABASE_URL")
    db_online = environ.get("db-online")

    if db_online == None:
        db_online = False
    
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
        if(path.isfile(FILEPATH+DB_NAME)):
            remove(FILEPATH+DB_NAME)
    
    app.config['SECRET_KEY'] = 'mySecretKey'
    app.config['SQLALCHEMY_DATABASE_URI'] = uri or f'sqlite:///{DB_NAME}' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    migrate = Migrate(app=app,db=db)
    db.init_app(app)
    
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

    return app