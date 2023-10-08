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

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        for rock_type in ROCKS:
            db.session.add(models.RockType(name=rock_type))
        for crux_type in CRUXES:
            db.session.add(models.Crux(name=crux_type))
        for level, (french, hueco) in enumerate(GRADES):
            db.session.add(models.Grade(level=level, french=french, hueco=hueco))
