from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///climbing_reports.db"
    db.init_app(app)

    from climbs.routes import routes

    app.register_blueprint(routes)

    return app
