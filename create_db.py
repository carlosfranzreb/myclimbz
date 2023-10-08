from argparse import ArgumentParser
from climbs import db, create_app, models


ROCKS = [
    "granite",
    "limestone",
    "sandstone",
    "basalt",
    "quartzite",
    "gneiss",
]

CRUXES = [
    "crimp",
    "sloper",
    "pocket",
    "tension",
    "compression",
    "heel hook",
    "toe hook",
    "undercling",
    "shoulder",
    "wrist",
    "drag",
    "power",
    "lock-off",
    "top out",
    "feet",
    "mantel",
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


def add_debug_data(db):
    db.session.add(models.Area(name="A1", rock_type_id=0))
    db.session.add(models.Area(name="A2", rock_type_id=1))

    db.session.add(models.Sector(name="A1_S1", area_id=0))
    db.session.add(models.Sector(name="A1_S2", area_id=0))
    db.session.add(models.Sector(name="A2_S1", area_id=1))

    db.session.add(
        models.Route(
            name="A1_S1_R1",
            sector_id=0,
            grade_id=8,
            height=3,
            landing=7,
            inclination=30,
        )
    )
    db.session.add(
        models.Route(name="A1_S1_R2", sector_id=0, grade_id=3, height=3, landing=7)
    )
    db.session.add(
        models.Route(
            name="A1_S2_R1", sector_id=1, grade_id=12, landing=4, inclination=-5
        )
    )
    db.session.add(
        models.Route(
            name="A2_S1_R1", sector_id=2, grade_id=15, height=6, inclination=40
        )
    )

    db.session.add(models.Session(date="2023-01-01", conditions=7, area_id=0))
    db.session.add(models.Session(date="2023-01-03", conditions=6, area_id=0))
    db.session.add(models.Session(date="2023-01-08", conditions=4, area_id=1))

    db.session.add(
        models.Climb(
            session_id=0, route_id=0, n_attempts=3, climbed=True, grade_felt_id=7
        )
    )
    db.session.add(models.Climb(session_id=0, route_id=1, n_attempts=12, climbed=False))
    db.session.add(models.Climb(session_id=1, route_id=1, n_attempts=5, climbed=True))
    db.session.add(
        models.Climb(
            session_id=2, route_id=3, n_attempts=1, climbed=True, grade_felt_id=14
        )
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--debug", type=bool, default=False)
    args = parser.parse_args()
    app = create_app(args.debug)
    with app.app_context():
        db.create_all()
        for rock_type in ROCKS:
            db.session.add(models.RockType(name=rock_type))
        for crux_type in CRUXES:
            db.session.add(models.Crux(name=crux_type))
        for level, (french, hueco) in enumerate(GRADES):
            db.session.add(models.Grade(level=level, french=french, hueco=hueco))

        if not args.debug:
            add_debug_data(db)
