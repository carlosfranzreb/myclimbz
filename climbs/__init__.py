from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(test=False, short=False):
    app = Flask(__name__)
    app.config[
        "SECRET_KEY"
    ] = "your-secret-key"  # replace 'your-secret-key' with your actual secret key
    csrf = CSRFProtect(app)

    if not test:
        db_name = "carlos"
    elif not short:
        db_name = "test"
    else:
        db_name = "test_short"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_name}.db"
    db.init_app(app)

    from climbs.blueprints.analysis.routes import analysis
    from climbs.blueprints.areas.routes import areas
    from climbs.blueprints.home.routes import home
    from climbs.blueprints.sessions.routes import sessions
    from climbs.blueprints.routes.routes import routes

    app.register_blueprint(areas)
    app.register_blueprint(analysis)
    app.register_blueprint(home)
    app.register_blueprint(sessions)
    app.register_blueprint(routes)

    return app
