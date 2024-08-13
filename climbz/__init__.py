import os
from importlib import import_module

from flask import Flask, request, redirect, url_for, session as flask_session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, login_user
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = "climbers.login"
login_manager.login_message_category = "info"


def create_app():
    app = Flask(__name__)
    # app.testing = os.environ.get("TESTING", "0") == "1"

    bcrypt.init_app(app)
    app.config["SECRET_KEY"] = os.environ.get("CLIMBZ_SECRET_KEY", "dev")
    app.config["RECAPTCHA_PUBLIC_KEY"] = os.environ["RECAPTCHA_PUBLIC_KEY"]
    app.config["RECAPTCHA_PRIVATE_KEY"] = os.environ["RECAPTCHA_PRIVATE_KEY"]
    CSRFProtect(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "CLIMBZ_DB_URI", "sqlite:///prod.db"
    )
    db.init_app(app)
    login_manager.init_app(app)

    app.config["MAIL_SERVER"] = "smtp-mail.outlook.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = os.environ["MAIL_USERNAME"]
    app.config["MAIL_PASSWORD"] = os.environ["MAIL_PASSWORD"]
    app.config["MAIL_DEBUG"] = True
    app.config["MAIL_SUPPRESS_SEND"] = False
    mail.init_app(app)

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

    # automatically login the user if defined in the environment
    disable_login = os.environ.get("DISABLE_LOGIN", "0") == "1"

    @app.before_request
    def check_request_validity():
        """
        - Ensure that the user is logged in before accessing any non-static page
        - If the page entails modifying an object, check that the user is allowed
            to do so
        """
        if not current_user.is_authenticated and disable_login:
            from climbz.models import Climber

            with app.test_request_context():
                climber = Climber.query.get(1)
                login_user(climber)

        if not request.endpoint:
            return
        elif (
            request.endpoint == "climbers.login"
            or request.endpoint == "climbers.register"
            or request.endpoint == "climbers.forgot_password"
            or request.endpoint == "home.guide"
            or "static" in request.endpoint
        ):
            return
        elif not current_user.is_authenticated:
            return redirect(url_for("climbers.login", next=request.endpoint))

        # check if the user is allowed to access the page
        if "edit" in request.endpoint or "delete" in request.endpoint:
            path, obj_id = request.path[1:].split("/")
            obj_str = path.split("_")[1]
            if obj_str == "project":
                return

            cls_str = obj_str.capitalize()
            if cls_str == "Password":
                cls_str = "Climber"
            cls = getattr(import_module("climbz.models"), cls_str)

            obj = cls.query.get(int(obj_id))
            if hasattr(obj, "created_by"):
                obj_owner = obj.created_by
            elif hasattr(obj, "climber_id"):
                obj_owner = obj.climber_id
            else:  # this is the case for climbers
                obj_owner = obj.id
            if (obj_owner != current_user.id and current_user.role != 1) or (
                current_user.role == 1 and cls_str in ["climb", "session"]
            ):
                flask_session["error"] = "You are not allowed to access this page."
                return redirect(flask_session.pop("call_from_url"))

    return app
