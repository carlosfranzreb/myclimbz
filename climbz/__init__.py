import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "climbers.login"
login_manager.login_message_category = "info"


def create_app():
    app = Flask(__name__)
    bcrypt.init_app(app)
    app.config["SECRET_KEY"] = os.urandom(24).hex()
    CSRFProtect(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "CLIMBZ_DB_URI", "sqlite:///prod.db"
    )
    db.init_app(app)
    login_manager.init_app(app)

    from climbz.blueprints.areas.routes import areas
    from climbz.blueprints.home.routes import home
    from climbz.blueprints.sessions.routes import sessions
    from climbz.blueprints.routes.routes import routes
    from climbz.blueprints.climbs.routes import climbs
    from climbz.blueprints.climbers.routes import climbers
    from climbz.blueprints.opinions.routes import opinions
    from climbz.blueprints.errors.handlers import errors

    app.register_blueprint(areas)
    app.register_blueprint(home)
    app.register_blueprint(sessions)
    app.register_blueprint(routes)
    app.register_blueprint(climbs)
    app.register_blueprint(climbers)
    app.register_blueprint(opinions)
    app.register_blueprint(errors)

    return app
