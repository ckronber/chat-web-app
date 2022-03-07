from django.shortcuts import redirect
from flask import Blueprint,request,jsonify,render_template
from flask_socketio import SocketIO,emit,send
from flask.helpers import url_for
from flask_login import login_required,current_user, logout_user
from itsdangerous import json
from numpy import broadcast
from .models import Note, User
from . import db
from threading import Lock
from datetime import datetime
#import json

async_mode = None
sio = SocketIO(async_mode=async_mode)

views = Blueprint('views', __name__)
thread = None
thread_lock = Lock()


#ONLINE/OFFLINE
#=====================================================================================
@sio.event
def update_ulist(online,userid):
    emit('up_user',{"status":online,"id":userid},broadcast=True)
    return jsonify({})

#ROUTE FOR HOME WEBPAGE
#========================================================================================
@views.route('/',methods=['GET'])
@views.route('/home',methods=['GET'])
@login_required
def home():
    myNotes = Note.query.all()
    users = User.query.all()
    return render_template('home.html',allNotes=myNotes,users = users,user=current_user,async_mode = sio.async_mode)


#ROUTE FOR ACCOUNT WEBPAGE
#========================================================================================
@views.route('/account',methods=['GET','POST']) 
@login_required
def account():
    return render_template('userSettings.html',user = current_user,async_mode = sio.async_mode)


#EVENTS FOR SOCKETIO SERVER

#@sio.event
#def my_event():
#    pass
    #emit('my_response',{'data': message['data']})

@sio.event
def getUser():
     emit('c_user',{'data': current_user.id,"user_name":current_user.user_name})

@sio.event
def my_broadcast_event(message):
    new_note = Note(data=message['data'], date = datetime.now(),user_id = current_user.id)
    db.session.add(new_note)
    db.session.commit()
    emit('message_add',{'user_name': current_user.user_name,'data': new_note.data, 'id':new_note.user_id} ,broadcast=True)
    load_all_messages()
    return jsonify({})

@sio.event
def loadHome():
    return  home()

@sio.event
def edit_event(message):
    noteEdit = Note.query.filter_by(id = message['id']).first()
    noteEdit.data = message['data']
    noteEdit.edited = True
    db.session.commit()
    emit('message_edit',{'id':noteEdit.msg_id ,'data':noteEdit.data})
    load_all_messages()
    return jsonify({})

@sio.event
def delete_event(message):
    noteDelete = Note.query.filter_by(id = message['id']).first()
    db.session.delete(noteDelete)
    db.session.commit()
    emit("delete_message",{"id":noteDelete.id},broadcast = True)
    load_all_messages()
    return jsonify({})

@sio.event
def load_all_messages():
    results = Note.query.all()
    emit("saved_messages",myResult=results, broadcast=True)
    return jsonify({})

#@sio.event
#def my_ping():
#     emit('my_pong')


#CONNECT AND DISCONNECT EVENTS
#=========================================================================
@sio.event
def connect():
    #global thread
    #with thread_lock:
    #    if thread is None:
    #        thread =  sio.start_background_task(background_thread)        
    update_ulist(True,current_user.id)
    print(f"{current_user.user_name} connected")
    online = User.query.filter_by(id = current_user.id).first()
    online.user_online = True
    db.session.commit()        
    
    print(online.user_online)
    return jsonify({})
    
    
@sio.event
def disconnect():
    print('Client disconnected', request.sid)
    update_ulist(False,current_user.id)
    online = User.query.filter_by(id = current_user.id).first()
    online.user_online = False
    db.session.commit()
    print(online.user_online)
    return jsonify({})

#edit and delete routes to pages that are not used
"""
@views.route('/delete-note', methods=['POST'])
@login_required
def deletenote():
    #session['receive_count'] = session.get('receive_count', 0) + 1
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})

@views.route('/edit-note', methods=['GET','POST'])
@login_required
def editNote():
    note = json.loads(request.data)
    print(f"{note['noteId']}: {note['note_data']}")
    noteId = note['noteId']
    note_data = note['note_data']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            if note_data:
                note.data = note_data
            db.session.commit()
    
    return jsonify({})
"""