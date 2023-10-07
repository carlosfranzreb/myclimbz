from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///climbing_reports.db"
    db = SQLAlchemy(app)
    db.init_app(app)

    from climbs.routes import home

    app.register_blueprint(home)

    return app
