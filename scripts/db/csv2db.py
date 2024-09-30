"""
This script adds climbs from a CSV sheet to the database.

The CSV sheet can have the following columns:
- Area: the name of the area.
- Sector: the name of the sector. Must be unique within the area.
- Boulder: the name of the boulder. Must be unique within the sector.
- Line: the name of the line. Must be unique within the boulder. In the DB, 
    line and boulder are merged into a single entity.
- Sit start: whether the line has a sit start ("yes" or "no").
- Grade: the grade of the line, in Font scale.
- Inclination: in degrees; an integer between -50 and 90 degrees.
- Height: in meters; a float with step 0.5 between 1 and 10 meters.
- Landing: an integer rating from 1 to 5.
- Rating: an integer rating from 1 to 10. We divide it by 2 and round it.
- Style (crux): the cruxes in our database are allowed.
- Date: the date of the climb, in the format "DD/MM/YYYY".
- Tries: the number of tries for the climb.
- Sent: whether the climb was sent ("yes" or "no").
- Grade felt: the grade felt by the climber, in Font scale. If this field is empty,
    the grade is taken from the "Grade" field.
- Video: a link to a video of the climb.
- Comments: any comments about the climb. They are added to the opinion comment.

We assume that the climbs of each route appear in chronological order in the CSV sheet,
meaning that the climb that appears first is the first time the climber tried the route.
We use this assumption to decide whether a send also counts as a flash.

If a CSV row doesn't comprise route information (from area to landing), it means that
this is another session on the same route. This is because the rows were merged in the
CSV. The opinion is taken from the last row of the route.
"""

import os
from argparse import ArgumentParser
from datetime import datetime
import csv

from climbz import db, create_app
from climbz.models import (
    Area,
    Route,
    Climb,
    Grade,
    Opinion,
    Sector,
    Session,
    Crux,
)


def add_climbs(csv_file: str, db, climber_id: int):

    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if len(row["Area"]) > 0:
                area_name = row["Area"].strip()
                area = Area.query.filter_by(name=area_name).first()
                if not area:
                    area = Area(name=area_name, created_by=climber_id)
                    db.session.add(area)
                    db.session.commit()

                sector = Sector.query.filter_by(
                    name=row["Sector"], area_id=area.id
                ).first()
                if not sector:
                    sector = Sector(
                        name=row["Sector"], area_id=area.id, created_by=climber_id
                    )
                    db.session.add(sector)
                    db.session.commit()

                route_name = ""
                if len(row["Boulder"]) > 0:
                    route_name = row["Boulder"]
                if len(row["Line"]) > 0:
                    if len(route_name) > 0:
                        route_name += " - "
                    route_name += row["Line"]

                route = Route.query.filter_by(
                    name=route_name, sector_id=sector.id
                ).first()
                if not route:
                    route = Route(
                        created_by=climber_id,
                        name=route_name,
                        sector_id=sector.id,
                        sit_start=row["Sit start"].lower() == "yes",
                        inclination=int(row["Inclination"]),
                        height=float(row["Height"]),
                    )
                    db.session.add(route)
                    db.session.commit()

                cruxes_str = row["Style (crux)"].split(", ")
                cruxes_obj = list()
                for crux_str in cruxes_str:
                    crux_str = crux_str.strip().capitalize()
                    crux = Crux.query.filter_by(name=crux_str).first()
                    if not crux and crux_str.endswith("s"):
                        crux = Crux.query.filter_by(name=crux_str[:-1]).first()
                    if not crux:
                        print(f"Crux {crux_str} not found in the database.")
                    else:
                        cruxes_obj.append(crux)

            date = datetime.strptime(row["Date"], "%d/%m/%Y")
            session = Session.query.filter_by(
                climber_id=climber_id, area_id=area.id, date=date.date()
            ).first()
            if session is None:
                session = Session(climber_id=climber_id, area_id=area.id, date=date)
                db.session.add(session)
                db.session.commit()

            previously_climbed = len(row["Area"]) == 0
            n_attempts = int(row["Tries"])
            sent = row["Sent"].lower() == "yes"
            climb = Climb(
                session_id=session.id,
                route_id=route.id,
                n_attempts=n_attempts,
                sent=sent,
                flashed=sent and not previously_climbed and n_attempts == 1,
                link=row["Video"],
                comment=row["Comments"],
            )
            db.session.add(climb)
            db.session.commit()

            opinion = Opinion.query.filter_by(
                climber_id=climber_id, route_id=route.id
            ).first()
            if opinion:
                if len(row["Comments"]) > 0:
                    opinion.comment = row["Comments"]
                if row["Video"]:
                    opinion.link = row["Video"]
            else:
                opinion = Opinion(
                    climber_id=climber_id,
                    route_id=route.id,
                    grade=Grade.query.filter_by(
                        font=row["Grade felt"] if row["Grade felt"] else row["Grade"]
                    ).first(),
                    landing=int(row["Landing"]) if row["Landing"] else None,
                    rating=round(int(row["Rating"]) / 2) if row["Rating"] else None,
                    cruxes=cruxes_obj,
                    comment=row["Comments"],
                )
                db.session.add(opinion)
            db.session.commit()


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", help="the CSV file to read")
    parser.add_argument("db_name", help="the SQLite database name to write to")
    parser.add_argument(
        "climber_id", type=int, help="the ID of the climber to add climbs for"
    )
    args = parser.parse_args()

    os.environ["CLIMBZ_DB_URI"] = f"sqlite:///{args.db_name}.db"
    os.environ["CLIMBZ_SECRET_KEY"] = os.urandom(24).hex()
    with create_app().app_context():
        add_climbs(args.csv_file, db, args.climber_id)
        db.session.close()
        print("Done.")
