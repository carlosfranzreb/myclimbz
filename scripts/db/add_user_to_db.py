"""Add user to existing database"""

from argparse import ArgumentParser
import os

from flask_bcrypt import generate_password_hash
from climbz import models, db, create_app


def add_user(email: str, name: str, pw: str) -> None:
    """
    Adds a user to the database.
    """

    # check if a user with that email already exists
    if models.Climber.query.filter_by(email=email).first():
        print(f"User with email {email} already exists.")
        return

    pw_hash = generate_password_hash(pw)
    db.session.add(models.Climber(name=name, email=email, password=pw_hash))
    db.session.commit()
    user_id = models.Climber.query.filter_by(email=email).first().id
    print(f"User {name} added to database with ID {user_id}")


if __name__ == "__main__":
    parser = ArgumentParser(description="Add user to existing database")
    parser.add_argument("db_name", help="Name of the database")
    parser.add_argument("email", help="User's email")
    parser.add_argument("name", help="User's name")
    parser.add_argument("pw", help="User's password")
    args = parser.parse_args()

    os.environ["CLIMBZ_DB_URI"] = f"sqlite:///{args.db_name}.db"
    os.environ["CLIMBZ_SECRET_KEY"] = os.urandom(24).hex()
    app = create_app()

    with app.app_context():
        add_user(args.email, args.name, args.pw)
