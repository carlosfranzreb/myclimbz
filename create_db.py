from argparse import ArgumentParser
from datetime import datetime
from climbs import db, create_app, models
import random


ROCKS = [
    "Granite",
    "Limestone",
    "Sandstone",
    "Basalt",
    "Quartzite",
    "Gneiss",
]

CRUXES = [
    "Crimp",
    "Sloper",
    "Pocket",
    "Tension",
    "Compression",
    "Heel hook",
    "Toe hook",
    "Undercling",
    "Shoulder",
    "Wrist",
    "Drag",
    "Power",
    "Lock-off",
    "Top out",
    "Feet",
    "Mantel",
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


def add_testing_data(db):
    print("Adding testing data")
    db.session.add(models.Area(name="A1", rock_type_id=1))
    db.session.add(models.Area(name="A2", rock_type_id=2))

    db.session.add(models.Sector(name="A1_S1", area_id=1))
    db.session.add(models.Sector(name="A1_S2", area_id=1))
    db.session.add(models.Sector(name="A2_S1", area_id=2))

    sector_ids = models.Sector.query.with_entities(models.Sector.id).distinct()
    sector_ids = [sector_id for sector_id, in sector_ids]

    with open("climb_names.txt", "r", encoding="utf-8") as f:
        for i, name in enumerate(f.readlines()):
            if i > 1995:
                break
            db.session.add(
                models.Route(
                    name=name.strip(),
                    sit_start=bool(i % 3),
                    sector_id=random.choice(sector_ids),
                    grade_id=i % 15 + 1,
                    height=i % 5 + 1,
                    landing=i % 10 + 1,
                    inclination=random.randrange(-10, 90, 5),
                    grade_felt_id=i % 24 + 1,
                    cruxes=[
                        models.Crux.query.filter_by(
                            name=CRUXES[random.randint(0, len(CRUXES) - 1)]
                        ).first()
                        for _ in range(random.randint(1, 5))
                    ],
                )
            )

    db.session.add(
        models.Route(
            name="A1_S1_R1",
            sit_start=False,
            sector_id=1,
            grade_id=8,
            height=3,
            landing=7,
            inclination=30,
            grade_felt_id=7,
            cruxes=[models.Crux.query.filter_by(name="Crimp").first()],
        )
    )
    db.session.add(
        models.Route(
            name="A1_S1_R2",
            sit_start=True,
            sector_id=1,
            grade_id=3,
            height=3,
            landing=7,
            cruxes=[
                models.Crux.query.filter_by(name="Crimp").first(),
                models.Crux.query.filter_by(name="Toe hook").first(),
            ],
        )
    )
    db.session.add(
        models.Route(
            name="A1_S2_R1",
            sit_start=True,
            sector_id=2,
            grade_id=12,
            landing=4,
            inclination=-5,
            grade_felt_id=13,
            cruxes=[models.Crux.query.filter_by(name="Heel hook").first()],
        )
    )
    db.session.add(
        models.Route(
            name="A2_S1_R1", sector_id=3, grade_id=15, height=6, inclination=40
        )
    )

    db.session.add(models.Session(date=datetime(2023, 1, 1), conditions=7, area_id=1))
    db.session.add(models.Session(date=datetime(2023, 1, 3), conditions=6, area_id=1))
    db.session.add(models.Session(date=datetime(2023, 1, 8), conditions=4, area_id=2))

    db.session.add(models.Climb(session_id=1, route_id=1, n_attempts=3, sent=True))
    db.session.add(models.Climb(session_id=1, route_id=2, n_attempts=12, sent=False))
    db.session.add(models.Climb(session_id=2, route_id=2, n_attempts=5, sent=True))
    db.session.add(models.Climb(session_id=3, route_id=4, n_attempts=1, sent=True))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--test", type=bool, default=False)
    args = parser.parse_args()
    app = create_app(args.test)
    with app.app_context():
        db.create_all()
        for rock_type in ROCKS:
            db.session.add(models.RockType(name=rock_type))
        for crux_type in CRUXES:
            db.session.add(models.Crux(name=crux_type))
        for level, (font, hueco) in enumerate(GRADES):
            db.session.add(models.Grade(level=level, font=font, hueco=hueco))

        if args.test is True:
            add_testing_data(db)

        db.session.commit()
