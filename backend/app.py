from flask import Flask
from config import Config
from database import db
from routes import api
from scheduler import start_scheduler

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(api)

    with app.app_context():
        db.create_all()
        # make sure the Arduino controller is initialised early so that
        # connection errors show up on startup rather than on first scan
        from arduino_service import get_gate_controller
        get_gate_controller()
        start_scheduler()

    return app

if __name__ == '__main__':
    app = create_app()
    # Run on 0.0.0.0 to be accessible by other devices
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
