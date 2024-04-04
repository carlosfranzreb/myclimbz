import os

from flask import Flask, request, redirect, url_for, session as flask_session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
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

    from climbz.models import Area, Climber, Climb, Opinion, Route, Session  # noqa

    @app.before_request
    def check_request_validity():
        """
        - Ensure that the user is logged in before accessing any non-static page
        - If the page entails modifying an object, check that the user is allowed to do so
        """
        if not request.endpoint:
            return
        elif request.endpoint == "climbers.login" or "static" in request.endpoint:
            return
        elif not current_user.is_authenticated:
            return redirect(url_for("climbers.login"))

        # check if the user is allowed to access the page
        if "edit" in request.endpoint or "delete" in request.endpoint:
            path, obj_id = request.path[1:].split("/")
            obj_str = path.split("_")[1]
            if obj_str == "project":
                return

            obj = eval(obj_str.capitalize()).query.get(int(obj_id))
            if hasattr(obj, "created_by"):
                obj_owner = obj.created_by
            elif hasattr(obj, "climber_id"):
                obj_owner = obj.climber_id
            else:  # this is the case for climbers
                obj_owner = obj.id
            if obj_owner != current_user.id and current_user.role != 1:
                flask_session["error"] = "You are not allowed to access this page."
                return redirect(flask_session.pop("call_from_url"))

    return app
