from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "climbers.login"
login_manager.login_message_category = "info"


def create_app(db_name: str):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = (
        "your-secret-key"  # replace 'your-secret-key' with your actual secret key
    )
    csrf = CSRFProtect(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_name}.db"
    db.init_app(app)
    login_manager.init_app(app)

    from climbz.blueprints.areas.routes import areas
    from climbz.blueprints.home.routes import home
    from climbz.blueprints.sessions.routes import sessions
    from climbz.blueprints.routes.routes import routes
    from climbz.blueprints.climbs.routes import climbs

    app.register_blueprint(areas)
    app.register_blueprint(home)
    app.register_blueprint(sessions)
    app.register_blueprint(routes)
    app.register_blueprint(climbs)

    return app
