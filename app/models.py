"""
Database models for the Meeting Notes App.
Defines User, Meeting, Note, and Attendee models.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """User model for authentication."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(64), unique=True, nullable=False, index=True
    )
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    meetings = db.relationship(
        'Meeting', backref='creator', lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary for JSON responses."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
            if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class Meeting(db.Model):
    """Meeting model - represents a meeting with notes and attendees."""
    
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    notes = db.relationship(
        'Note', backref='meeting', lazy='dynamic',
        cascade='all, delete-orphan'
    )
    attendees = db.relationship(
        'Attendee', backref='meeting', lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def to_dict(self, include_notes=False, include_attendees=False):
        """
        Convert meeting to dictionary for JSON responses.
        
        Args:
            include_notes: Include associated notes
            include_attendees: Include associated attendees
        """
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'location': self.location,
            'created_at': self.created_at.isoformat()
            if self.created_at else None,
            'updated_at': self.updated_at.isoformat()
            if self.updated_at else None,
            'user_id': self.user_id,
            'creator_username': self.creator.username if self.creator else None
        }
        
        if include_notes:
            data['notes'] = [note.to_dict() for note in self.notes]
        
        if include_attendees:
            data['attendees'] = [
                attendee.to_dict() for attendee in self.attendees
            ]
        
        return data
    
    def __repr__(self):
        return f'<Meeting {self.title}>'


class Note(db.Model):
    """
    Note model - represents a note linked to a meeting
    (supports Markdown).
    """
    
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Foreign key
    meeting_id = db.Column(
        db.Integer, db.ForeignKey('meetings.id'), nullable=False
    )
    
    def to_dict(self):
        """Convert note to dictionary for JSON responses."""
        return {
            'id': self.id,
            'content': self.content,
            'meeting_id': self.meeting_id,
            'created_at': self.created_at.isoformat()
            if self.created_at else None,
            'updated_at': self.updated_at.isoformat()
            if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Note {self.id} for Meeting {self.meeting_id}>'


class Attendee(db.Model):
    """Attendee model - represents a person attending a meeting."""
    
    __tablename__ = 'attendees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    meeting_id = db.Column(
        db.Integer, db.ForeignKey('meetings.id'), nullable=False
    )
    
    def to_dict(self):
        """Convert attendee to dictionary for JSON responses."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'meeting_id': self.meeting_id,
            'created_at': self.created_at.isoformat()
            if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Attendee {self.name}>'
