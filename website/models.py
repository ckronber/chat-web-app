import enum
from datetime import date, datetime
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from . import db

# Standard lengths
EMAIL_MAX_LEN = 254       # RFC 3696: max email length is 254 chars
PASS_MAX_LEN = 255        # Safe for bcrypt/scrypt/argon2/pbkdf2 hashes (160+ chars)
NAME_MAX_LEN = 100        # Reasonable for names; adjust if needed
DESC_MAX_LEN = 1000       # For short bios, not full text blobs
DATA_MAX_LEN = 10000      # For notes or JSON-like data

# Enumerations (stored as strings in DB unless you use PostgreSQL + native enum)
class GenderEnum(enum.Enum):
    male = "Male"
    female = "Female"

class RelationshipStatusEnum(enum.Enum):
    single_mingle = "Single and Ready to Mingle"
    single = "Single"
    complicated = "It's Complicated"
    open_rel = "Open Relationship"
    relationship = "In Relationship"
    married = "Married"

# Models

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(DATA_MAX_LEN), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    edited = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    # Optional: Many-to-many if you want to allow note sharing later
    # users_shared_with = db.relationship("User", secondary=note_users_table, ...)

    def __repr__(self):
        return f"<Note id={self.id} user_id={self.user_id}>"

    @staticmethod
    def format_timestamp(dt: datetime, fmt: int = 1) -> str:
        """Format a datetime for display (0 = ISO, 1 = MM/DD/YYYY HH:MM:SS, etc.)"""
        if not dt:
            return "N/A"
        
        parts = {
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": dt.hour,
            "minute": dt.minute,
            "second": dt.second,
        }

        if fmt == 1:  # e.g. 04/05/2025  13:30:45
            return f"{parts['month']:02}/{parts['day']:02}/{parts['year']} {parts['hour']:02}:{parts['minute']:02}:{parts['second']:02}"
        elif fmt == 2:  # e.g. 13:30:45
            return f"{parts['hour']:02}:{parts['minute']:02}:{parts['second']:02}"
        elif fmt == 3:  # e.g. 04/05/2025
            return f"{parts['month']:02}/{parts['day']:02}/{parts['year']}"
        else:  # default ISO format
            return dt.isoformat()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # Auth & Identity
    email = db.Column(db.String(EMAIL_MAX_LEN), unique=True, nullable=False)
    password = db.Column(db.String(PASS_MAX_LEN), nullable=False)
    username = db.Column(db.String(NAME_MAX_LEN), unique=True, nullable=False)
    display_name = db.Column(db.String(NAME_MAX_LEN))  # Optional: for profile title
    image_url = db.Column(db.String(500), default=None)  # Store URL or relative path

    # Profile
    birth_date = db.Column(db.Date, nullable=True)  # Use Date instead of DateTime
    first_name = db.Column(db.String(NAME_MAX_LEN))
    last_name = db.Column(db.String(NAME_MAX_LEN))
    marriage_date = db.Column(db.Date, nullable=True)
    interests = db.Column(db.Text)          # Use Text for longer lists (JSON or comma-separated)
    bio = db.Column(db.String(DESC_MAX_LEN))  # Short description

    gender = db.Column(db.Enum(GenderEnum), nullable=True)
    relationship_status = db.Column(db.Enum(RelationshipStatusEnum), nullable=True)

    online = db.Column(db.Boolean, default=False, nullable=False)  # Renamed for clarity

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Relationships
    notes = db.relationship('Note', backref='user', cascade="all, delete-orphan", lazy='dynamic')
    channels = db.relationship('Channel', backref='owner', cascade="all, delete-orphan", lazy='dynamic')

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}' user_name='{self.username}'>"

    @property
    def full_name(self) -> str:
        """Return first + last name, or username if not set."""
        parts = [self.first_name or '', self.last_name or '']
        name = ' '.join(filter(None, parts))
        return name or self.username


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(NAME_MAX_LEN), unique=True, nullable=False)
    description = db.Column(db.String(DESC_MAX_LEN))  # No need for `unique` here unless enforced by app logic
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"<Channel id={self.id} name='{self.name}' owner_id={self.owner_id}>"