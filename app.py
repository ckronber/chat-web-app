# app.py (or __init__.py if using package pattern)
from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from website.auth import auth as auth_blueprint
from website.views import views  # assuming your main routes are in views.py 
from website.extensions import sio

db = SQLAlchemy()   
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'  # replace with env var
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
    
    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(views)

    return app

# 👇 crucial: define user_loader once at module level
@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

app = create_app()

PORT = 5000
HOST = "localhost"
SSLCERT = ["C:\\Users\\ckron\\cert.pem", "C:\\Users\\ckron\\key.pem"]

if __name__ == '__main__':
    if PORT == 443:
        sio.run(app,debug=True,port=PORT,host=HOST,certfile=SSLCERT[0],keyfile=SSLCERT[1],server_side=True)
    else:
        sio.run(app,debug=True,host=HOST,port=PORT,allow_unsafe_werkzeug=True)
