# views.py (main routes + socket handlers)

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import User, Message
from .extensions import sio 

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html', user=current_user)

# 🔹 Socket.IO connection handling
@sio.on('connect')
def handle_connect(auth=None):
    if not current_user.is_authenticated:
        emit('auth_fail', {'message': 'Not authenticated'})
        return False  # disconnect client
    
    join_room(str(current_user.id))  # optional: per-user room

@views.route('/api/online_users')
@login_required
def online_users():
    users = User.query.filter_by(user_online=True).all()
    return jsonify([{
        'id': u.id,
        'username': u.user_name
    } for u in users])

# 🔹 Socket.IO emit to all clients when a user joins (e.g., after login)
@sio.on('join')
def on_join(data):
    username = data.get('username', 'Anonymous')
    room = data.get('room', 'general')
    join_room(room)
    sio.emit('status', {'msg': f'{username} has joined the room.'}, room=room)

# 🔹 Handle chat messages
@sio.on('send_message')
def handle_send_message(data):
    msg_content = data.get('message')
    if not msg_content or not current_user.is_authenticated:
        emit('error', {'message': 'Unauthorized or empty message'})
        return

    # Save to DB
    msg = Message(content=msg_content, user_id=current_user.id)
    db.session.add(msg)
    db.session.commit()

    # Emit to room
    sio.emit(
        'new_message',
        {
            'id': current_user.id,
            'username': current_user.user_name,
            'message': msg_content,
            'timestamp': msg.timestamp.isoformat()
        },
        room=data.get('room', 'general')
    )

# 🔹 Broadcast new user on signup (optional — but handled in auth now)