from website import create_app
#from flask_socketio import SocketIO
from website.views import sio
app = create_app()
sio.init_app(app)
PORT = 443
#PORT = 5000
HOST = "localhost"
MYCERT = "C:\\Users\\ckron\\cert.pem"
MYKEY = "C:\\Users\\ckron\\key.pem"

if __name__ == "__main__":
    if PORT == 443:
        sio.run(app,port=PORT,host=HOST,certfile=MYCERT,keyfile=MYKEY,server_side=True,debug=True)
    else:
        sio.run(app,debug=True,host=HOST,port=PORT)
    #sio.run(app,debug=True,port=80,host=HOST)
    #sio.run(app,debug=True,host=HOST,port=PORT