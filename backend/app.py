from flask import Flask
from config import Config
from database import db
from routes import api
from models import BlockLimit
from scheduler import start_scheduler

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

        if not BlockLimit.query.first():
            defaults = {'A': 15, 'D1': 15, 'D2': 15, 'B': 10, 'C': 10}
            for b, m in defaults.items():
                db.session.add(BlockLimit(block_name=b, minutes=m))
            db.session.commit()

        start_scheduler()

    return app

if __name__ == '__main__':
    app = create_app()
    # Run on 0.0.0.0 to be accessible by other devices
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
