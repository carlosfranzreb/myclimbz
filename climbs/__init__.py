from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(debug=False):
    app = Flask(__name__)

    db_name = "climbs" if not debug else "debug"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_name}.db"
    db.init_app(app)

    from climbs.analysis.routes import analysis
    from climbs.areas.routes import areas
    from climbs.sessions.routes import sessions
    from climbs.routes.routes import routes

    app.register_blueprint(areas)
    app.register_blueprint(analysis)
    app.register_blueprint(sessions)
    app.register_blueprint(routes)

    return app
