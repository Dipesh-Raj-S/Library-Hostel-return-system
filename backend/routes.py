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
    block = data.get('block')

    if not name or not face_encoding or not block:
        return jsonify({'error': 'Missing name, face_encoding, or block'}), 400

    # Check if student already exists (optional, by name for now)
    existing = Student.query.filter_by(name=name).first()
    if existing:
        return jsonify({'error': 'Student already exists'}), 400

    new_student = Student(
        name=name,
        face_encoding=json.dumps(face_encoding),
        block=block
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
            'block': student.block,
            'encoding': json.loads(student.face_encoding)
        }
    return jsonify(encodings), 200

@api.route('/scan_library', methods=['POST'])
def scan_library():
    data = request.json
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({'error': 'Missing student_id'}), 400

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Check for active trip
    active_trip = Trip.query.filter_by(student_id=student_id, status='active').first()

    if active_trip:
        if active_trip.direction == "Hostel -> Library":
            # ARRIVAL at Library: End the "Hostel -> Library" timer
            active_trip.end_time = datetime.now()
            
            # Check for late
            if active_trip.end_time > active_trip.expected_end_time:
                active_trip.status = 'late'
                active_trip.is_alert = True
                active_trip.exceeded_limit = True
            else:
                active_trip.status = 'completed'
            
            db.session.commit()
            cancel_trip_check(active_trip.id)
            
            return jsonify({
                'message': 'Journey "Hostel -> Library" completed.',
                'status': active_trip.status,
                'open_gate': True
            }), 200
            
        elif active_trip.direction == "Library -> Hostel":
             # Already detected at Library recently, ignore or debounce
             return jsonify({'message': 'Timer "Library -> Hostel" already running.', 'open_gate': False}), 200
    
    # START new trip: Library -> Hostel
    # Calculate duration
    block = student.block.upper()
    if block in ['A', 'D1', 'D2']:
        duration_minutes = 15
    elif block in ['B', 'C']:
        duration_minutes = 10
    else:
        duration_minutes = 10 

    start_time = datetime.now()
    expected_end_time = start_time + timedelta(minutes=duration_minutes)

    new_trip = Trip(
        student_id=student_id,
        start_time=start_time,
        expected_end_time=expected_end_time,
        status='active',
        direction="Library -> Hostel",
        start_location="Library",
        end_location="Hostel"
    )
    db.session.add(new_trip)
    db.session.commit()

    schedule_trip_check(current_app._get_current_object(), new_trip.id, expected_end_time)

    return jsonify({
        'message': 'Started timer "Library -> Hostel"',
        'trip_id': new_trip.id,
        'expected_end_time': expected_end_time.isoformat(),
        'open_gate': True
    }), 201


@api.route('/scan_hostel', methods=['POST'])
def scan_hostel():
    data = request.json
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'error': 'Missing student_id'}), 400

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    # Check for active trip
    active_trip = Trip.query.filter_by(student_id=student_id, status='active').first()

    if active_trip:
        if active_trip.direction == "Library -> Hostel":
            # ARRIVAL at Hostel: End the "Library -> Hostel" timer
            active_trip.end_time = datetime.now()
            
            if active_trip.end_time > active_trip.expected_end_time:
                active_trip.status = 'late'
                active_trip.is_alert = True
                active_trip.exceeded_limit = True
            else:
                active_trip.status = 'completed'
            
            db.session.commit()
            cancel_trip_check(active_trip.id)
            
            return jsonify({
                'message': 'Journey "Library -> Hostel" completed.',
                'status': active_trip.status,
                'open_gate': True
            }), 200
        
        elif active_trip.direction == "Hostel -> Library":
            # Already active, recently started
             return jsonify({'message': 'Timer "Hostel -> Library" already running.', 'open_gate': False}), 200

    # START new trip: Hostel -> Library
    # Calculate duration (SAME limits apply)
    block = student.block.upper()
    if block in ['A', 'D1', 'D2']:
        duration_minutes = 15
    elif block in ['B', 'C']:
        duration_minutes = 10
    else:
        duration_minutes = 10 

    start_time = datetime.now()
    expected_end_time = start_time + timedelta(minutes=duration_minutes)

    new_trip = Trip(
        student_id=student_id,
        start_time=start_time,
        expected_end_time=expected_end_time,
        status='active',
        direction="Hostel -> Library",
        start_location="Hostel",
        end_location="Library"
    )
    db.session.add(new_trip)
    db.session.commit()

    schedule_trip_check(current_app._get_current_object(), new_trip.id, expected_end_time)

    return jsonify({
        'message': 'Started timer "Hostel -> Library"',
        'trip_id': new_trip.id,
        'expected_end_time': expected_end_time.isoformat(),
        'open_gate': True
    }), 201

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
