from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
from database import db
from models import Trip

scheduler = BackgroundScheduler()

def check_trip_expiry(app, trip_id):
    """
    Callback function to check if a trip has expired (student is late).
    """
    with app.app_context():
        trip = Trip.query.get(trip_id)
        if trip and trip.status == 'active':
            trip.status = 'late'
            trip.is_alert = True
            db.session.commit()
            print(f"ALERT: Trip {trip_id} for Student {trip.student.name} is LATE!")

def start_scheduler():
    if not scheduler.running:
        scheduler.start()

def schedule_trip_check(app, trip_id, run_date):
    """
    Schedules a check for the trip at the expected end time.
    """
    scheduler.add_job(
        func=check_trip_expiry,
        trigger=DateTrigger(run_date=run_date),
        args=[app, trip_id],
        id=str(trip_id),
        replace_existing=True
    )

def cancel_trip_check(trip_id):
    """
    Cancels the scheduled check if the student arrives on time.
    """
    job_id = str(trip_id)
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
