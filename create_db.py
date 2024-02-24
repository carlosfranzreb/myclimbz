"""
Script to create the database and populate it with testing data.
"""

from argparse import ArgumentParser
from datetime import datetime
import random

from flask_sqlalchemy import SQLAlchemy

from climbz import db, create_app, models


ROCKS = [
    "Granite",
    "Limestone",
    "Sandstone",
    "Basalt",
    "Quartzite",
    "Gneiss",
]

CRUXES = [
    # Hands
    "Crimp",
    "Drag",
    "Pinch",
    "Pocket",
    "Sloper",
    # Legs
    "Drop knee",
    "Feet",
    "Heel hook",
    "Knee bar",
    "Toe hook",
    # Hold orientation
    "Gaston",
    "Sidepull",
    "Undercling",
    # Other
    "Compression",
    "Dyno",
    "Endurance",
    "Lock-off",
    "Mantel",
    "Power",
    "Scary",
    "Tension",
]

GRADES = [
    ("3", "VB"),
    ("3+", "VB"),
    ("4", "V0"),
    ("4+", "V0"),
    ("5", "V1"),
    ("5+", "V1"),
    ("6A", "V2"),
    ("6A+", "V3"),
    ("6B", "V4"),
    ("6B+", "V5"),
    ("6C", "V6"),
    ("6C+", "V6"),
    ("7A", "V7"),
    ("7A+", "V7"),
    ("7B", "V8"),
    ("7B+", "V8"),
    ("7C", "V9"),
    ("7C+", "V10"),
    ("8A", "V11"),
    ("8A+", "V12"),
    ("8B", "V13"),
    ("8B+", "V14"),
    ("8C", "V15"),
    ("8C+", "V16"),
    ("9A", "V17"),
    ("9A+", "V18"),
    ("9B", "V19"),
]


def add_testing_data(db: SQLAlchemy, n_routes: int) -> None:
    """
    Adds `n_routes` routes to the database. The route names are read from
    `climb_names.txt`. The routes are distributed among 2 areas, and their
    characteristics are randomly generated.

    The routes are added to 4 sessions, 3 in area 1 and 1 in area 2, with
    a probability of 0.8. For area 1, there is a probability of 0.2 that a
    route is added to a second session.
    """
    print("Adding testing data")
    db.session.add(models.Climber(name="Climber1", email="c@d", password="123"))
    db.session.add(models.Climber(name="Climber2", email="b@d", password="123"))

    db.session.add(models.Area(name="A1", rock_type_id=1, created_by=1))
    db.session.add(models.Area(name="A2", rock_type_id=2, created_by=2))

    db.session.add(models.Sector(name="A1_S1", area_id=1, created_by=1))
    db.session.add(models.Sector(name="A1_S2", area_id=1, created_by=2))
    db.session.add(models.Sector(name="A2_S1", area_id=2, created_by=2))
    sector_ids = list(range(1, 4))

    # create 4 sessions: 3 in A1, 1 in A2
    db.session.add(
        models.Session(date=datetime(2023, 1, 1), conditions=4, area_id=1, climber_id=1)
    )
    db.session.add(
        models.Session(
            date=datetime(2023, 1, 13), conditions=2, area_id=1, climber_id=1
        )
    )
    db.session.add(
        models.Session(date=datetime(2023, 3, 7), conditions=1, area_id=1, climber_id=1)
    )
    db.session.add(
        models.Session(
            date=datetime(2023, 8, 18), conditions=4, area_id=2, climber_id=2
        )
    )

    with open("instance/utils/climb_names.txt", "r", encoding="utf-8") as f:
        for route_idx, name in enumerate(f.readlines()):
            if route_idx > n_routes:
                break
            sector_id = random.choice(sector_ids)
            area_id = 1 if sector_id < 3 else 2
            db.session.add(
                models.Route(
                    name=name.strip(),
                    sit_start=bool(route_idx % 3),
                    sector_id=sector_id,
                    height=route_idx % 5 + 1,
                    inclination=random.randrange(-10, 90, 5),
                    created_by=random.choice([1, 2]),
                )
            )
            # with p=0.6, add climb to the session
            if random.random() < 0.6:
                session_id = random.randint(1, 3) if area_id == 1 else 4
                sent = bool(random.randint(0, 1))
                climber_id = 1 if session_id < 4 else 2
                db.session.add(
                    models.Climb(
                        session_id=session_id,
                        route_id=route_idx + 1,
                        n_attempts=random.randint(1, 10),
                        sent=sent,
                        flashed=bool(random.randint(0, 1)) if sent else False,
                        climber_id=climber_id,
                    )
                )
                # for area 1, with p=0.2, add climb to a second session
                if area_id == 1 and random.random() < 0.2:
                    remaining_sessions = list(range(1, 4))
                    remaining_sessions.remove(session_id)
                    session_id = random.choice(remaining_sessions)
                    db.session.add(
                        models.Climb(
                            session_id=session_id,
                            route_id=route_idx + 1,
                            n_attempts=random.randint(1, 10),
                            sent=bool(random.randint(0, 1)),
                            flashed=False,
                            climber_id=climber_id,
                        )
                    )

                # add climber opinion for the route
                db.session.add(
                    models.Opinion(
                        route_id=route_idx + 1,
                        climber_id=climber_id,
                        grade_id=random.randint(1, len(GRADES)),
                        landing=random.randint(1, 5),
                        rating=random.randint(1, 5),
                        cruxes=[
                            models.Crux.query.filter_by(
                                name=CRUXES[random.randint(0, len(CRUXES) - 1)]
                            ).first()
                            for _ in range(random.randint(1, 5))
                        ],
                    )
                )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--n-routes", type=int, default=100, required=False)
    args = parser.parse_args()
    if args.test is True:
        db_name = f"test_{args.n_routes}"
    else:
        db_name = "prod"
    app = create_app(db_name)
    with app.app_context():
        db.create_all()
        for rock_type in ROCKS:
            db.session.add(models.RockType(name=rock_type))
        for crux_type in CRUXES:
            db.session.add(models.Crux(name=crux_type))
        for level, (font, hueco) in enumerate(GRADES):
            db.session.add(models.Grade(level=level, font=font, hueco=hueco))

        if args.test is True:
            add_testing_data(db, args.n_routes)

        db.session.commit()
