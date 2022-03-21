from website import create_app
from website.views import sio,async_mode

app,db_online = create_app()

if(db_online == True):
    async_mode = "gevent"
else:
    async_mode = "eventlet"

sio.init_app(app)
PORTS = [443,5000]
PORT = PORTS[1]
HOST = "localhost"
SSLCERT = ["C:\\Users\\ckron\\cert.pem", "C:\\Users\\ckron\\key.pem"]

if __name__ == "__main__":
    if(db_online):
        app.run()
    else:
        if PORT == 443:
            sio.run(app,debug=True,port=PORT,host=HOST,certfile=SSLCERT[0],keyfile=SSLCERT[1],server_side=True)
        else:
            sio.run(app,debug=True,host=HOST,port=PORT)