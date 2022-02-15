#from sqlalchemy.sql.functions import user
import asyncio
import enum
from email.policy import default
from msilib.schema import File
from tkinter.tix import FileEntry
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
#from flask_migrate import Migrate
from . import db

EMAIL_LENGTH = PASS_LENGTH = NAME_LENGTH = 150
DATA_LENGTH = 10000

class GenderEnum(enum.Enum):
    male = "Male"
    female = "Female"
    nonbinary = "Non-Binary"

class RelationshipStatus(enum.Enum):
    single_mingle = "Single and Ready to Mingle"
    single = "Single"
    comp = "It's Complicated"
    open_rel = "Open Relationship"
    rel = "In Relationship"
    married = "Married"

class GenInterest(enum.Enum):
    straight = "Straight"
    gay = "Gay"

class Note(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    data = db.Column(db.String(DATA_LENGTH))
    date = db.Column(db.DateTime(timezone=True),default=func.now)
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
    user_online = db.Column(db.Boolean,default=False,nullable=False)
    email = db.Column(db.String(EMAIL_LENGTH), unique = True) # max length, unique means only unique emails
    password = db.Column(db.String(PASS_LENGTH))
    image = db.Column(db.String(),default=None)
    birth_date = db.Column(db.DateTime(timezone=True))
    first_name = db.Column(db.String(NAME_LENGTH),default=None)
    last_name = db.Column(db.String(NAME_LENGTH),default=None) 
    user_name = db.Column(db.String(NAME_LENGTH))
    marriage_date = db.Column(db.DateTime(timezone = True))
    interests = db.Column(db.String(DATA_LENGTH))
    description = db.Column(db.String(DATA_LENGTH))
    gender = db.Column(db.Enum(GenderEnum))
    gender_interest = db.Column(db.Enum(GenInterest))
    relationship_status = db.Column(db.Enum(RelationshipStatus))
    notes = db.relationship('Note',backref = 'user',cascade = "all, delete, delete-orphan", lazy = 'dynamic')
    #noteUsers = db.relationship('Note', backref='user',cascade = "all, delete, delete-orphan",lazy = 'dynamic')
    channels = db.relationship('Channel', backref = 'user', cascade = "all, delete, delete-orphan", lazy = 'dynamic')
    
    def __repr__(self):
        return f"id: {self.id}: email: {self.email} user: {self.first_name}"


class Channel(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(NAME_LENGTH), unique = True)
    description = db.Column(db.String(NAME_LENGTH), unique = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f"id: {self.id}: Channel Name: {self.name} Channel Description: {self.description}"