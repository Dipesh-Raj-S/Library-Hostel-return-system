from flask import Blueprint, request, jsonify, current_app, render_template
from models import Student, Trip, db
from scheduler import schedule_trip_check, cancel_trip_check
from datetime import datetime, timedelta
import json
from arduino_service import open_hostel_gate, open_library_gate

api = Blueprint('api', __name__)

TRIP_LIMITS = {
    'A': 15, 'D1': 15, 'D2': 15,
    'B': 10, 'C': 10
}
DEFAULT_LIMIT = 10

@api.route('/')
def home():
    return render_template('index.html')

@api.route('/check-student/<regno>', methods=['GET'])
def check_student(regno):
    student = Student.query.filter_by(regno=regno).first()
    if student:
        return {"message": "Exists"}, 200
    return {"message": "Available"}, 404

@api.route('/register_student', methods=['POST'])
def register_student():
    data = request.json
    name = data.get('name')
    face_encoding = data.get('face_encoding') # List of floats
    block = data.get('block')
    regno = data.get('reg_no')

    if not name or not face_encoding or not block or not regno:
        return jsonify({'error': 'Missing Fields'}), 400

    # Check if student already exists 
    existing = Student.query.filter_by(regno=regno).first()
    if existing:
        return jsonify({'error': 'Student with regno already exists'}), 400

    new_student = Student(
        name=name,
        face_encoding=json.dumps(face_encoding),
        block=block,
        regno=regno
    )
    db.session.add(new_student)
    db.session.commit()

    return jsonify({'message': 'Student registered successfully', 'student_id': new_student.id}), 201

@api.route('/delete-student/<regno>', methods=['DELETE'])
def delete_student(regno):
    student = Student.query.filter_by(regno=regno).first()
    if student:
        db.session.delete(student)
        db.session.commit()
        return {"message": "Deleted"}, 200
    return {"message": "Not found"}, 404

@api.route('/get_encodings', methods=['GET'])
def get_encodings():
    students = Student.query.all()
    encodings = {}
    for student in students:
        encodings[student.id] = {
            'name': student.name,
            'block': student.block,
            'reg_no':student.regno,
            'encoding': json.loads(student.face_encoding)
        }
    return jsonify(encodings), 200
def process_scan(student_id, current_location):
    target_location = "Library" if current_location == "Hostel" else "Hostel"
    direction_label = f"{current_location} -> {target_location}"
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Atomic check for active trips
    active_trip = Trip.query.filter_by(student_id=student_id, status='active').first()

    if active_trip:
        # Check if they are arriving at the destination of their current trip
        if active_trip.end_location == current_location:
            active_trip.end_time = datetime.now()
            
            # lateness
            is_late = active_trip.end_time > active_trip.expected_end_time
            active_trip.status = 'late' if is_late else 'completed'
            active_trip.is_alert = is_late
            active_trip.exceeded_limit = is_late
            
            db.session.commit()
            cancel_trip_check(active_trip.id)
            
            if current_location == "Hostel":
                open_hostel_gate()
            else:
                open_library_gate()
            
            return jsonify({
                'message': f'Journey to {current_location} completed.',
                'status': active_trip.status,
                'open_gate': True
            }), 200
        
        # If they scan again at the same starting location, ignore
        return jsonify({'message': 'Trip already in progress', 'open_gate': False}), 200

    # Start new trip
    duration = TRIP_LIMITS.get(student.block.upper(), DEFAULT_LIMIT)
    start_time = datetime.now()
    expected_end_time = start_time + timedelta(minutes=duration)

    new_trip = Trip(
        student_id=student_id,
        start_time=start_time,
        expected_end_time=expected_end_time,
        status='active',
        direction=direction_label,
        start_location=current_location,
        end_location=target_location
    )
    
    db.session.add(new_trip)
    db.session.commit()

    # Schedule the background alert
    schedule_trip_check(current_app._get_current_object(), new_trip.id, expected_end_time)
    
    if current_location == "Hostel":
        open_hostel_gate()
    else:
        open_library_gate()

    return jsonify({
        'message': f'Started timer: {direction_label}',
        'trip_id': new_trip.id,
        'open_gate': True
    }), 201

@api.route('/scan_library', methods=['POST'])
def scan_library():
    return process_scan(request.json.get('student_id'), "Library")

@api.route('/scan_hostel', methods=['POST'])
def scan_hostel():
    return process_scan(request.json.get('student_id'), "Hostel")

@api.route('/active_timers', methods=['GET'])
def active_timers():
    trips = Trip.query.filter_by(status='active').all()
    return jsonify([t.to_dict() for t in trips]), 200

@api.route('/alerts', methods=['GET'])
def alerts():
    # Return all late trips (active or completed but late)
    # Actually, if it's 'late', it stays 'late'.
    late_trips = Trip.query.filter_by(is_alert=True).order_by(Trip.expected_end_time.desc()).all()
    return jsonify([t.to_dict() for t in late_trips]), 200
