"""
Formats the names of the areas, sectors, and routes in the database to conform to the
conventions defined by the `format_name` function in the `climbz/forms/utils.py` file.
"""

import os
from argparse import ArgumentParser

from myclimbz import db, create_app
from myclimbz.models import Area, Route, Sector
from myclimbz.forms.utils import format_name


def format_names(db) -> None:
    """
    Iterate over all route names, sector names and area names in the database and
    format them.
    """
    for table in [Area, Sector, Route]:
        for obj in table.query.all():
            new_name = format_name(obj.name)
            if new_name == obj.name:
                continue
            existing_obj = Sector.query.filter_by(name=new_name).first()
            if existing_obj is not None:
                print(f"Sector {obj.name} already exists.")
                print(f"\tID of wrongly-formatted object: {obj.id}")
                print(f"\tID of correctly-formatted obj: {existing_obj.id}")
            else:
                obj.name = new_name
                db.session.add(obj)
        db.session.commit()


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("db_name", help="the SQLite database name to write to")
    args = parser.parse_args()

    os.environ["CLIMBZ_DB_URI"] = f"sqlite:///{args.db_name}.db"
    os.environ["CLIMBZ_SECRET_KEY"] = os.urandom(24).hex()
    with create_app().app_context():
        format_names(db)
        db.session.close()
        print("Done.")
