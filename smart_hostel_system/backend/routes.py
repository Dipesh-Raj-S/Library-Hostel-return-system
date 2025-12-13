from flask import Blueprint, request, jsonify, current_app, render_template
from models import Student, Trip, db
from scheduler import schedule_trip_check, cancel_trip_check
from datetime import datetime, timedelta
import json

api = Blueprint('api', __name__)

@api.route('/')
def home():
    return render_template('index.html')

@api.route('/register_student', methods=['POST'])
def register_student():
    data = request.json
    name = data.get('name')
    face_encoding = data.get('face_encoding') # List of floats

    if not name or not face_encoding:
        return jsonify({'error': 'Missing name or face_encoding'}), 400

    # Check if student already exists (optional, by name for now)
    existing = Student.query.filter_by(name=name).first()
    if existing:
        return jsonify({'error': 'Student already exists'}), 400

    new_student = Student(
        name=name,
        face_encoding=json.dumps(face_encoding)
    )
    db.session.add(new_student)
    db.session.commit()

    return jsonify({'message': 'Student registered successfully', 'student_id': new_student.id}), 201

@api.route('/get_encodings', methods=['GET'])
def get_encodings():
    students = Student.query.all()
    encodings = {}
    for student in students:
        encodings[student.id] = {
            'name': student.name,
            'encoding': json.loads(student.face_encoding)
        }
    return jsonify(encodings), 200

@api.route('/library_exit', methods=['POST'])
def library_exit():
    data = request.json
    student_id = data.get('student_id')
    duration_minutes = data.get('duration_minutes', 10) # Default 10 mins

    if not student_id:
        return jsonify({'error': 'Missing student_id'}), 400

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Check if there is already an active trip
    active_trip = Trip.query.filter_by(student_id=student_id, status='active').first()
    if active_trip:
        return jsonify({'message': 'Trip already active', 'trip_id': active_trip.id}), 200

    start_time = datetime.now()
    expected_end_time = start_time + timedelta(minutes=duration_minutes)

    new_trip = Trip(
        student_id=student_id,
        start_time=start_time,
        expected_end_time=expected_end_time,
        status='active'
    )
    db.session.add(new_trip)
    db.session.commit()

    # Schedule the timer check
    schedule_trip_check(current_app._get_current_object(), new_trip.id, expected_end_time)

    return jsonify({
        'message': 'Trip started',
        'trip_id': new_trip.id,
        'expected_end_time': expected_end_time.isoformat()
    }), 201

@api.route('/hostel_entry', methods=['POST'])
def hostel_entry():
    data = request.json
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'error': 'Missing student_id'}), 400

    # Find active trip
    trip = Trip.query.filter_by(student_id=student_id, status='active').first()
    
    if not trip:
        # If no active trip, maybe just open the gate anyway? Or deny?
        # For this project, let's assume valid entry but log it or just return OK.
        # But strictly, if they didn't exit library, maybe they are just entering normally.
        # Let's return a specific message so the client knows.
        return jsonify({'message': 'No active library trip found, but entry allowed', 'open_gate': True}), 200

    trip.end_time = datetime.now()
    
    # Check if late (redundant if scheduler hasn't fired, but good for immediate feedback)
    if trip.end_time > trip.expected_end_time:
        trip.status = 'late'
        trip.is_alert = True
    else:
        trip.status = 'completed'
    
    db.session.commit()

    # Cancel the scheduled check
    cancel_trip_check(trip.id)

    return jsonify({'message': 'Trip completed', 'status': trip.status, 'open_gate': True}), 200

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
