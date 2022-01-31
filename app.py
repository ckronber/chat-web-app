from website import create_app
from website.views import sio

#This port is used for local testing
PORT = 5000

#This port is used when testing on a domain
#PORT = 443

HOST = "localhost"

app = create_app()
sio.init_app(app)
#client = socketio.test_client(app)

if __name__ == "__main__":
    #app.run(app,debug=True,port=PORT,host=HOST)
    #sio.run(app,debug=True,port=PORT,host=HOST,keyfile = 'C:\\Users\ckron\key.pem', certfile='C:\\Users\ckron\cert.pem')
    sio.run(app,debug=True,port=PORT,host=HOST)