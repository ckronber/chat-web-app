from website.views import app

#This port is used when testing on a domain
##PORT = 80
#PORT = 443
PORT = 5000

HOST = "0.0.0.0"
#HOST = "localhost"
MYCERT = "C:\\Users\\ckron\\cert.pem"
MYKEY = "C:\\Users\\ckron\\key.pem"
#CERT = ".\\chat-app\cert.pem"
#KEY= ".\\chat-app\key.pem"
#sio.init_app(app)
#client = socketio.test_client(app)
if __name__ == "__main__":
    app.run(debug=True,host=HOST,port=PORT)
    #ssl_context = (CERT,KEY))
    #sio.run(app,port=PORT,host=HOST,certfile=MYCERT,keyfile=MYKEY,server_side=True,debug=True)
    #sio.run(app,debug=True,port=80,host=HOST)
    #sio.run(app,debug=True,host=HOST,port=PORT)