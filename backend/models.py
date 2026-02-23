from datetime import datetime
from database import db
import json

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Storing face encoding as a JSON string (list of floats)
    face_encoding = db.Column(db.Text, nullable=False)
    block = db.Column(db.String(10), nullable=False) # A, B, C, D1, D2
    regno = db.Column(db.String(50),nullable=False,unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'block': self.block,
            'reg_no':self.regno,
            'created_at': self.created_at.isoformat()
        }

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now)
    expected_end_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active', index=True)  # active, completed, late
    
    # New fields for bi-directional tracking
    direction = db.Column(db.String(50), nullable=False) # "Hostel -> Library" or "Library -> Hostel"
    start_location = db.Column(db.String(50), nullable=False) # "Hostel" or "Library"
    end_location = db.Column(db.String(50), nullable=False) # "Library" or "Hostel"
    exceeded_limit = db.Column(db.Boolean, default=False)
    
    is_alert = db.Column(db.Boolean, default=False, index=True)

    student = db.relationship('Student', backref=db.backref('trips', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name,
            'reg_no':self.student.regno,
            'student_block': self.student.block,
            'start_time': self.start_time.isoformat(),
            'expected_end_time': self.expected_end_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'direction': self.direction,
            'start_location': self.start_location,
            'end_location': self.end_location,
            'exceeded_limit': self.exceeded_limit,
            'is_alert': self.is_alert
        }
