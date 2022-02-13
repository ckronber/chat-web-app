from asyncio import sslproto
from distutils.util import convert_path
from ssl import CERT_REQUIRED
from website import create_app
from website.views import sio


#This port is used when testing on a domain
#PORT = 5000
#PORT = 80
#PORT = 443
HOST = "0.0.0.0"
#HOST = "localhost"
#CERT = "C:\\Users\ckron\cert.pem"
#KEY= "C:\\Users\ckron\key.pem"
CERT = ".\\chat-app\cert.pem"
KEY= ".\\chat-app\key.pem"

app = create_app()
sio.init_app(app,ssl_context = (CERT,KEY))
#client = socketio.test_client(app)

if __name__ == "__main__":
   # app.run(debug=True)
    #sio.run(app,debug=True,port=PORT,host=HOST)
    sio.run(app,debug=True,port=8000,host=HOST)
    #sio.run(app,debug=True,host=HOST,port=PORT)