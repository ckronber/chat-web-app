from website import create_app
from website.views import sio
from gevent.pywsgi import WSGIServer
import os

#added to the app and is ready for push

app = create_app()
database_online = os.environ.get("db-online")
sio.init_app(app)

PORTS = [443,5000]
PORT = PORTS[1]
HOST = "localhost"
SSLCERT = ["C:\\Users\\ckron\\cert.pem", "C:\\Users\\ckron\\key.pem"]

if __name__ == "__main__":
    if(database_online == "True"):
        app.run(host="ckronberg-web-app.herokuapp.com",port = 11457)
    else:
        if PORT == 443:
            sio.run(app,debug=True,port=PORT,host=HOST,certfile=SSLCERT[0],keyfile=SSLCERT[1],server_side=True)
        else:
            sio.run(app,debug=True,host=HOST,port=PORT)
