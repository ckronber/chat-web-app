from flask import Blueprint, request, jsonify, render_template, redirect, flash
from flask_socketio import SocketIO, emit, send
from flask.helpers import url_for
from flask_login import login_required, current_user, logout_user
from threading import Lock
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from .models import Note, User, DirectMessage
from . import db

database_online = os.environ.get("db-online")

# if  database_online == "True":
#   async_mode = "gevent"
# else:
async_mode = "eventlet"

sio = SocketIO(cors_allowed_origins="*")
sio.asyc_mode = async_mode
views = Blueprint("views", __name__)
thread = None
thread_lock = Lock()


# ROUTE FOR HOME WEBPAGE
# ========================================================================================
@views.route("/", methods=["GET"])
@views.route("/home", methods=["GET"])
@login_required
def home():
    myNotes = Note.query.all()
    users = User.query.all()
    return render_template(
        "home.html",
        allNotes=myNotes,
        users=users,
        user=current_user,
        async_mode=sio.async_mode,
    )


# ROUTE FOR ACCOUNT WEBPAGE
# ========================================================================================
@views.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        user = User.query.filter_by(id=current_user.id).first()
        if user:
            user.user_name = request.form.get("user_name", user.user_name)
            user.first_name = request.form.get("first_name", user.first_name)
            user.last_name = request.form.get("last_name", user.last_name)
            user.email = request.form.get("email", user.email)

            birth_date = request.form.get("birth_date")
            if birth_date:
                from datetime import datetime

                user.birth_date = datetime.strptime(birth_date, "%Y-%m-%d")

            gender = request.form.get("gender")
            if gender:
                from .models import GenderEnum

                try:
                    user.gender = GenderEnum[gender]
                except KeyError:
                    pass

            rel_status = request.form.get("relationship_status")
            if rel_status:
                from .models import RelationshipStatus

                status_mapping = {
                    "single": RelationshipStatus.single,
                    "rel": RelationshipStatus.rel,
                    "married": RelationshipStatus.married,
                    "comp": RelationshipStatus.comp,
                    "open_rel": RelationshipStatus.open_rel,
                }
                if rel_status in status_mapping:
                    user.relationship_status = status_mapping[rel_status]

            marriage_date = request.form.get("marriage_date")
            if marriage_date:
                from datetime import datetime

                user.marriage_date = datetime.strptime(marriage_date, "%Y-%m-%d")

            user.interests = request.form.get("interests", user.interests)
            user.description = request.form.get("description", user.description)

            db.session.commit()

    return render_template(
        "userSettings.html", user=current_user, async_mode=sio.async_mode
    )


# ROUTE FOR USER PROFILE PAGE
# ========================================================================================
@views.route("/user/<int:user_id>")
@login_required
def user_profile(user_id):
    profile_user = User.query.get_or_404(user_id)
    user_notes = Note.query.filter_by(user_id=user_id).all()
    return render_template(
        "userProfile.html",
        profile_user=profile_user,
        user_notes=user_notes,
        user=current_user,
    )


# ROUTE FOR UPLOADING PROFILE IMAGE
# ========================================================================================
@views.route("/upload-image", methods=["POST"])
@login_required
def upload_image():
    from flask import current_app
    import uuid

    print("=== UPLOAD DEBUG ===")
    print(f"Root path: {current_app.root_path}")
    print(f"Static folder: {current_app.static_folder}")
    print(f"Files in request: {list(request.files.keys())}")

    if "profile_image" not in request.files:
        print("ERROR: No file in request!")
        flash("No file selected", "error")
        return redirect("/account")

    file = request.files["profile_image"]
    print(f"File received: {file.filename}")

    if file.filename == "":
        print("ERROR: Empty filename!")
        flash("No file selected", "error")
        return redirect("/account")

    allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}

    # Get file extension
    ext = ""
    if "." in file.filename:
        ext = file.filename.rsplit(".", 1)[1].lower()

    print(f"Extension: {ext}")

    if ext not in allowed_extensions:
        print("ERROR: Invalid extension!")
        flash("File type not allowed", "error")
        return redirect("/account")

    # Create unique filename
    filename = f"{current_user.id}_{uuid.uuid4().hex}.{ext}"

    # Use static folder path
    upload_folder = os.path.join(current_app.static_folder, "uploads")
    print(f"Upload folder: {upload_folder}")

    # Create directory if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)

    # Save the file
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    print(f"File saved to: {filepath}")
    print(f"File exists: {os.path.exists(filepath)}")

    # Update database
    user = User.query.get(current_user.id)
    if user:
        # Delete old image if exists
        if user.image:
            old_filepath = os.path.join(upload_folder, user.image)
            if os.path.exists(old_filepath):
                os.remove(old_filepath)

        user.image = filename
        db.session.commit()
        print(f"Database updated with: {filename}")

    flash("Profile image updated!", "success")
    return redirect("/account")

    file = request.files["profile_image"]
    print(f"File received: {file.filename}")

    if file.filename == "":
        flash("No file selected", "error")
        return redirect("/account")

    if file:
        allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}

        # Get file extension
        if "." in file.filename:
            ext = file.filename.rsplit(".", 1)[1].lower()
        else:
            ext = ""

        if ext not in allowed_extensions:
            flash("File type not allowed", "error")
            return redirect("/account")

        # Create unique filename
        filename = f"{current_user.id}_{uuid.uuid4().hex}.{ext}"

        # Use a fixed path for uploads
        upload_folder = os.path.join(
            os.path.dirname(current_app.root_path), "website", "static", "uploads"
        )
        print(f"Upload folder: {upload_folder}")

        # Create directory if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)

        # Save the file
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        print(f"File saved to: {filepath}")
        print(f"File exists: {os.path.exists(filepath)}")

        # Update database
        user = User.query.get(current_user.id)
        if user:
            # Delete old image if exists
            if user.image:
                old_filepath = os.path.join(upload_folder, user.image)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)

            user.image = filename
            db.session.commit()
            print(f"Database updated with: {filename}")

        flash("Profile image updated!", "success")
        return redirect("/account")

    return redirect("/account")


# ROUTE FOR UPLOADING DM FILES
# ========================================================================================
@views.route("/upload-dm-file", methods=["POST"])
@login_required
def upload_dm_file():
    from flask import current_app
    import uuid
    import traceback

    print("=== DM FILE UPLOAD START ===")

    try:
        if "dm_file" not in request.files:
            print("ERROR: No dm_file in request")
            return jsonify({"error": "No file selected"}), 400

        file = request.files["dm_file"]
        to_user = request.form.get("to_user")
        to_user_id = request.form.get("to_user_id")
        message_text = request.form.get("message_text", "")

        print(f"File: {file.filename}, to_user: {to_user}, to_user_id: {to_user_id}")

        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        allowed_image_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
        allowed_file_extensions = {
            "png",
            "jpg",
            "jpeg",
            "gif",
            "webp",
            "pdf",
            "doc",
            "docx",
            "txt",
            "mp3",
            "mp4",
            "wav",
            "mov",
            "avi",
        }

        if "." in file.filename:
            ext = file.filename.rsplit(".", 1)[1].lower()
        else:
            ext = ""

        is_image = ext in allowed_image_extensions
        allowed_extensions = (
            allowed_image_extensions if is_image else allowed_file_extensions
        )

        if ext not in allowed_extensions:
            return jsonify({"error": "File type not allowed"}), 400

        filename = f"dm_{current_user.id}_{uuid.uuid4().hex}.{ext}"
        upload_folder = os.path.join(current_app.static_folder, "dm_uploads")
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        print(f"File saved: {filepath}")

        recipient = User.query.filter_by(user_name=to_user).first()
        if not recipient:
            recipient = User.query.get(int(to_user_id) if to_user_id else None)

        print(f"Recipient: {recipient}")

        if recipient:
            dm = DirectMessage()
            dm.data = message_text
            dm.date = datetime.now()
            dm.sender_id = current_user.id
            dm.recipient_id = recipient.id
            dm.file_url = f"/static/dm_uploads/{filename}"
            dm.file_name = file.filename
            dm.file_type = "image" if is_image else "file"
            db.session.add(dm)
            db.session.commit()
            print(f"DM created: {dm.id}")

            dm_data = {
                "id": dm.id,
                "sender_id": current_user.id,
                "sender_name": current_user.user_name,
                "recipient_id": recipient.id,
                "recipient_name": recipient.user_name,
                "data": dm.data,
                "date": dm.date.strftime("%Y-%m-%d %H:%M:%S"),
                "is_deleted": dm.is_deleted,
                "deleted_date": None,
                "edited": dm.edited,
                "edited_date": None,
                "file_url": dm.file_url,
                "file_name": dm.file_name,
                "file_type": dm.file_type,
            }

            try:
                emit("dm_message", dm_data, broadcast=True)
            except Exception as emit_error:
                print(f"Emit warning (non-critical): {emit_error}")

            print("=== DM FILE UPLOAD SUCCESS ===")
            return jsonify({"success": True, "dm_data": dm_data})
        else:
            print("ERROR: Recipient not found")
            return jsonify({"error": "Recipient not found"}), 400

    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ONLINE/OFFLINE
# =====================================================================================
@sio.event
def update_ulist(online, userid):
    emit("up_user", {"status": online, "id": userid}, broadcast=True)
    return jsonify({})


# EVENTS FOR SOCKETIO SERVER
# =========================================================================================

# @sio.event
# def start_background_task():
# pass
# emit('my_response',{'data': message['data']})


@sio.event
def getUser():
    emit("c_user", {"data": current_user.id, "user_name": current_user.user_name})


@sio.event
def my_broadcast_event(message):

    # Replacing <, > and / so there can not be injection of html into the chat
    for hChar in ["<", ">", "/"]:
        message["data"] = message["data"].replace(hChar, "")

    new_note = Note(data=message["data"], date=datetime.now(), user_id=current_user.id)
    db.session.add(new_note)
    db.session.commit()
    emit(
        "message_add",
        {
            "user_name": current_user.user_name,
            "data": new_note.data,
            "id": new_note.user_id,
            "noteID": new_note.id,
        },
        broadcast=True,
    )
    return jsonify({})


@sio.event
def loadHome():
    return home()


@sio.event
def edit_event(message):
    noteEdit = Note.query.filter_by(id=message["id"]).first()
    noteEdit.data = message["data"]
    noteEdit.edited = True
    noteEdit.edited_date = datetime.now()
    db.session.commit()

    emit(
        "edit_message",
        {
            "user_name": current_user.user_name,
            "noteID": message["id"],
            "data": message["data"],
            "edited": True,
            "edited_date": noteEdit.edited_date.strftime("%Y-%m-%d %H:%M:%S"),
        },
        broadcast=True,
    )
    return jsonify({})


@sio.event
def delete_event(message):
    emit("delete_message", {"id": message["id"]}, broadcast=True)
    noteDelete = Note.query.filter_by(id=message["id"]).first()
    db.session.delete(noteDelete)
    db.session.commit()


@sio.event
def dm_event(message):
    for hChar in ["<", ">", "/"]:
        message["data"] = message["data"].replace(hChar, "")

    recipient = User.query.filter_by(user_name=message["toUser"]).first()
    if recipient:
        dm = DirectMessage()
        dm.data = message["data"]
        dm.date = datetime.now()
        dm.sender_id = current_user.id
        dm.recipient_id = recipient.id
        db.session.add(dm)
        db.session.commit()

        dm_data = {
            "id": dm.id,
            "sender_id": current_user.id,
            "sender_name": current_user.user_name,
            "recipient_id": recipient.id,
            "recipient_name": recipient.user_name,
            "data": dm.data,
            "date": dm.date.strftime("%Y-%m-%d %H:%M:%S"),
            "is_deleted": dm.is_deleted,
            "deleted_date": None,
            "edited": dm.edited,
            "edited_date": None,
        }

        emit("dm_message", dm_data, broadcast=True)

    return jsonify({})


@sio.event
def delete_dm_event(message):
    dm_id = message.get("id")
    dm = DirectMessage.query.get(dm_id)

    if dm and dm.sender_id == current_user.id:
        dm.is_deleted = True
        dm.deleted_date = datetime.now()
        db.session.commit()

        emit(
            "dm_deleted",
            {
                "id": dm.id,
                "deleted_date": dm.deleted_date.strftime("%Y-%m-%d %H:%M:%S"),
            },
            broadcast=True,
        )

    return jsonify({})


@sio.event
def edit_dm_event(message):
    dm_id = message.get("id")
    dm = DirectMessage.query.get(dm_id)

    if dm and dm.sender_id == current_user.id:
        for hChar in ["<", ">", "/"]:
            message["data"] = message["data"].replace(hChar, "")

        dm.data = message["data"]
        dm.edited = True
        dm.edited_date = datetime.now()
        db.session.commit()

        emit(
            "dm_edited",
            {
                "id": dm.id,
                "data": dm.data,
                "edited": True,
                "edited_date": dm.edited_date.strftime("%Y-%m-%d %H:%M:%S"),
            },
            broadcast=True,
        )

    return jsonify({})


@sio.event
def get_dm_history(message):
    other_user_id = int(message["userId"])
    my_id = current_user.id

    dms_sent = DirectMessage.query.filter_by(
        sender_id=my_id, recipient_id=other_user_id
    ).all()
    dms_received = DirectMessage.query.filter_by(
        sender_id=other_user_id, recipient_id=my_id
    ).all()

    unread_count = 0
    all_dms = []
    for dm in dms_sent:
        all_dms.append(
            {
                "id": dm.id,
                "sender_id": dm.sender_id,
                "sender_name": current_user.user_name,
                "recipient_id": dm.recipient_id,
                "recipient_name": message["userName"],
                "data": dm.data,
                "date": dm.date.strftime("%Y-%m-%d %H:%M:%S"),
                "is_deleted": dm.is_deleted,
                "deleted_date": dm.deleted_date.strftime("%Y-%m-%d %H:%M:%S")
                if dm.deleted_date
                else None,
                "edited": dm.edited,
                "edited_date": dm.edited_date.strftime("%Y-%m-%d %H:%M:%S")
                if dm.edited_date
                else None,
                "file_url": dm.file_url,
                "file_name": dm.file_name,
                "file_type": dm.file_type,
            }
        )
    for dm in dms_received:
        if not dm.is_read:
            dm.is_read = True
            unread_count += 1
        all_dms.append(
            {
                "id": dm.id,
                "sender_id": dm.sender_id,
                "sender_name": message["userName"],
                "recipient_id": dm.recipient_id,
                "data": dm.data,
                "date": dm.date.strftime("%Y-%m-%d %H:%M:%S"),
                "is_deleted": dm.is_deleted,
                "deleted_date": dm.deleted_date.strftime("%Y-%m-%d %H:%M:%S")
                if dm.deleted_date
                else None,
                "edited": dm.edited,
                "edited_date": dm.edited_date.strftime("%Y-%m-%d %H:%M:%S")
                if dm.edited_date
                else None,
                "file_url": dm.file_url,
                "file_name": dm.file_name,
                "file_type": dm.file_type,
            }
        )

    if unread_count > 0:
        db.session.commit()

    all_dms.sort(key=lambda x: x["date"])

    emit(
        "dm_history",
        {
            "messages": all_dms,
            "withUser": message["userName"],
            "withUserId": other_user_id,
        },
    )
    return jsonify({})


@sio.event
def load_all_messages():
    results = Note.query.all()
    emit("saved_messages", myResult=results, broadcast=True)
    return jsonify({})


@sio.event
def load_all_dms():
    my_id = current_user.id

    dms_sent = DirectMessage.query.filter_by(sender_id=my_id).all()
    dms_received = DirectMessage.query.filter_by(recipient_id=my_id).all()

    all_dms = []
    for dm in dms_sent:
        sender = User.query.get(dm.sender_id)
        recipient = User.query.get(dm.recipient_id)
        all_dms.append(
            {
                "id": dm.id,
                "sender_id": dm.sender_id,
                "sender_name": sender.user_name if sender else "Unknown",
                "recipient_id": dm.recipient_id,
                "recipient_name": recipient.user_name if recipient else "Unknown",
                "data": dm.data,
                "date": dm.date.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    for dm in dms_received:
        if dm.sender_id != my_id:
            sender = User.query.get(dm.sender_id)
            recipient = User.query.get(dm.recipient_id)
            all_dms.append(
                {
                    "id": dm.id,
                    "sender_id": dm.sender_id,
                    "sender_name": sender.user_name if sender else "Unknown",
                    "recipient_id": dm.recipient_id,
                    "recipient_name": recipient.user_name if recipient else "Unknown",
                    "data": dm.data,
                    "date": dm.date.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

    all_dms.sort(key=lambda x: x["date"])

    emit("dm_history", {"messages": all_dms})
    return jsonify({})


@sio.event
def get_dm_conversations():
    my_id = current_user.id

    conversations = {}

    dms_received = DirectMessage.query.filter_by(recipient_id=my_id).all()
    for dm in dms_received:
        other_user_id = dm.sender_id
        if other_user_id not in conversations:
            sender = User.query.get(other_user_id)
            conversations[other_user_id] = {
                "user_id": other_user_id,
                "user_name": sender.user_name if sender else "Unknown",
                "last_message": dm.data,
                "last_date": dm.date.strftime("%Y-%m-%d %H:%M:%S"),
                "unread_count": 0,
            }
        if not dm.is_read:
            conversations[other_user_id]["unread_count"] += 1

    dms_sent = DirectMessage.query.filter_by(sender_id=my_id).all()
    for dm in dms_sent:
        other_user_id = dm.recipient_id
        if other_user_id not in conversations:
            recipient = User.query.get(other_user_id)
            conversations[other_user_id] = {
                "user_id": other_user_id,
                "user_name": recipient.user_name if recipient else "Unknown",
                "last_message": dm.data,
                "last_date": dm.date.strftime("%Y-%m-%d %H:%M:%S"),
                "unread_count": 0,
            }
        else:
            dm_date = datetime.strptime(
                dm.date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"
            )
            conv_date = datetime.strptime(
                conversations[other_user_id]["last_date"], "%Y-%m-%d %H:%M:%S"
            )
            if dm_date > conv_date:
                conversations[other_user_id]["last_message"] = dm.data
                conversations[other_user_id]["last_date"] = dm.date.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

    conv_list = list(conversations.values())
    conv_list.sort(key=lambda x: x["last_date"], reverse=True)

    emit("dm_conversations", {"conversations": conv_list})
    return jsonify({})


@sio.event
def mark_dm_read(data):
    my_id = current_user.id
    other_user_id = data.get("userId")

    unread_dms = DirectMessage.query.filter_by(
        sender_id=other_user_id, recipient_id=my_id, is_read=False
    ).all()

    for dm in unread_dms:
        dm.is_read = True

    db.session.commit()

    total_unread = DirectMessage.query.filter_by(
        recipient_id=my_id, is_read=False
    ).count()

    emit("dm_read_receipt", {"userId": other_user_id, "total_unread": total_unread})
    return jsonify({})


@sio.event
def get_total_unread_dms():
    my_id = current_user.id
    total_unread = DirectMessage.query.filter_by(
        recipient_id=my_id, is_read=False
    ).count()
    emit("total_unread_dms", {"count": total_unread})
    return jsonify({})


# @sio.event
# def my_ping():
#     emit('my_pong')


# CONNECT AND DISCONNECT EVENTS
# =========================================================================
@sio.event
def connect():
    update_ulist(True, current_user.id)
    print(f"{current_user.user_name} connected")
    online = User.query.filter_by(id=current_user.id).first()
    online.user_online = True
    db.session.commit()

    print(online.user_online)
    return jsonify({})


@sio.event
def disconnect():
    print("Client disconnected", request.sid)
    update_ulist(False, current_user.id)
    online = User.query.filter_by(id=current_user.id).first()
    online.user_online = False
    db.session.commit()
    print(online.user_online)
    return jsonify({})


# edit and delete routes to pages that are not used
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
