from climbs import db, create_app
from climbs.models.crux import Crux
from climbs.models.rock_type import RockType


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

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        for rock_type in ROCKS:
            db.session.add(RockType(name=rock_type))
        for crux_type in CRUXES:
            db.session.add(Crux(name=crux_type))
