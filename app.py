from website import create_app
from website.views import sio
import os

app = create_app()
database_online = os.environ.get("db-online")
sio.init_app(app)

#* Here are the ports that are used
PORTS = [443,5000]
PORT = PORTS[1]
HOST = "localhost"
SSLCERT = ["C:\\Users\\ckron\\cert.pem", "C:\\Users\\ckron\\key.pem"]

#* This is the main function to start the server
if __name__ == "__main__":
    if(database_online == "True"):
        app.run(cors_allowed_origins='*')
    else:
        if PORT == 443:
            sio.run(app,debug=True,port=PORT,host=HOST,certfile=SSLCERT[0],keyfile=SSLCERT[1],server_side=True)
        else:
            sio.run(app,debug=True,host=HOST,port=PORT)