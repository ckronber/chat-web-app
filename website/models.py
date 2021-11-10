from sqlalchemy.sql.functions import user
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from . import db

EMAIL_LENGTH = PASS_LENGTH = NAME_LENGTH = 150
DATA_LENGTH = 10000

class Note(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    data = db.Column(db.String(DATA_LENGTH))
    date = db.Column(db.DateTime(timezone = True),default=func.now)
    edited = db.Column(db.Boolean,default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_list = db.relationship('Noteusers', backref='note',cascade = "all, delete, delete-orphan", lazy = 'dynamic')

    def __repr__(self):
        return f"id: {self.id}: date: {self.date} user: {self.user_id}"

    def set_time_format(time_format:int):
        time_stamp = {"year":datetime.now().year,"month":datetime.now().month,"day":datetime.now().day,"hour":datetime.now().hour,"minute":datetime.now().minute,"second":datetime.now().second}

        if(time_format == 1):
            return f"{time_stamp['month']}/{time_stamp['day']}/{time_stamp['year']}  {time_stamp['hour']}:{time_stamp['minute']}:{time_stamp['second']}"
        if(time_format == 2):
            return f"{time_stamp['hour']}:{time_stamp['minute']}:{time_stamp['second']}"
        
        if(time_format == 3):
            return f"{time_stamp['month']}/{time_stamp['day']}/{time_stamp['year']}"

class Noteusers(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(NAME_LENGTH), unique=True)
    user_id = db.Column(db.Integer,db.ForeignKey("note.id"))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    #note_id = db.Column(db.Integer,db.ForeignKey("note.id"))
    noteuser_id = db.Column(db.Integer,db.ForeignKey("noteusers.id"))
    email = db.Column(db.String(EMAIL_LENGTH), unique = True) # max length, unique means only unique emails
    password = db.Column(db.String(PASS_LENGTH))
    first_name = db.Column(db.String(NAME_LENGTH))
    notes = db.relationship('Note',backref = 'user',cascade = "all, delete, delete-orphan", lazy = 'dynamic')
    #noteUsers = db.relationship('Note', backref='user',cascade = "all, delete, delete-orphan",lazy = 'dynamic')
    channels = db.relationship('Channel', backref = 'user', cascade = "all, delete, delete-orphan", lazy = 'dynamic')
    teams = db.relationship('Team', backref = 'user', cascade = "all, delete, delete-orphan", lazy = 'dynamic')
    
    def __repr__(self):
        return f"id: {self.id}: email: {self.first_name} user: {self.email}"

class Channel(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(NAME_LENGTH), unique = True)
    description = db.Column(db.String(NAME_LENGTH), unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team_users = db.relationship('TeamUsers',backref = 'channel', cascade = "all, delete, delete-orphan", lazy = 'dynamic')
    

    def __repr__(self):
        return f"id: {self.id}: Channel Name: {self.name} Channel Description: {self.description}"

class Team(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(NAME_LENGTH), unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team_users = db.relationship('TeamUsers',backref = 'team', cascade = "all, delete, delete-orphan", lazy = 'dynamic')

    def __repr__(self):
        return f"id: {self.id}: TeamName: {self.name}"

class TeamUsers(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(NAME_LENGTH), unique = True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))