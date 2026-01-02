from datetime import datetime
from database import db
import json

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Storing face encoding as a JSON string (list of floats)
    face_encoding = db.Column(db.Text, nullable=False)
    block = db.Column(db.String(10), nullable=False) # A, B, C, D1, D2
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'block': self.block,
            'created_at': self.created_at.isoformat()
        }

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now)
    expected_end_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active') # active, completed, late
    is_alert = db.Column(db.Boolean, default=False)

    student = db.relationship('Student', backref=db.backref('trips', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name,
            'student_block': self.student.block,
            'start_time': self.start_time.isoformat(),
            'expected_end_time': self.expected_end_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'is_alert': self.is_alert
        }
