from distutils.util import convert_path
from smtplib import SMTP_SSL_PORT
from website import create_app
from website.views import sio

#This port is used when testing on a domain
#PORT = 5000
#PORT = 80
#PORT = 443

HOST = "0.0.0.0"
#HOST = "localhost"
#my_CERT = "C:\\Users\ckron\cert.pem"
#my_KEY= "C:\\Users\ckron\key.pem"
#CERT = ".\\chat-app\cert.pem"
#KEY= ".\\chat-app\key.pem"
app = create_app()
sio.init_app(app)
#client = socketio.test_client(app)

if __name__ == "__main__":
    #app.run(sio,debug=True,ssl_context = (CERT,KEY))
    #sio.run(app,debug=True,port=PORT,host=HOST)
    sio.run(app,debug=True,port=80,host=HOST)
    #sio.run(app,debug=True,host=HOST,port=PORT)