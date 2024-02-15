"""
Test that the object deletions cascade correctly.
"""

from datetime import datetime

from climbz.models import Area, Sector, Session, Route, Climb
from climbz import db


def create_objects() -> dict:
    """
    Create an area with a sector, routes and a session and climbs. Return them
    as a dict of objects.
    """
    # create an area, and add a route and a session on that route to it
    objects = dict()
    objects["area"] = Area(name="Test Area", rock_type_id=1)
    objects["sector"] = Sector(name="Test Sector", area=objects["area"])
    objects["route"] = Route(name="Test Route", sector=objects["sector"], grade_id=1)
    objects["session"] = Session(
        date=datetime.now(), conditions=1, area=objects["area"]
    )
    objects["climb"] = Climb(
        session=objects["session"], route=objects["route"], n_attempts=5, sent=True
    )

    db.session.add_all(objects.values())
    db.session.commit()
    return objects


def check_deletions(object_ids: dict, deleted_keys: list) -> None:
    """
    Check that the objects with the given keys have been deleted.
    """
    for cls_str, obj_id in object_ids.items():
        if "_" in cls_str:
            cls_name = cls_str[: cls_str.index("_")].capitalize()
        else:
            cls_name = cls_str.capitalize()
        cls = globals()[cls_name.capitalize()]
        obj = cls.query.filter_by(id=obj_id).first()
        if cls_str in deleted_keys:
            assert obj is None, f"{cls_str} with id {obj_id} was not deleted"
        else:
            assert obj is not None, f"{cls_str} with id {obj_id} was deleted"


def test_delete_area(test_client_db) -> None:
    """
    When deleting an area, all its sectors, routes, sessions and climbs should be
    deleted as well.
    """
    objects = create_objects()
    object_ids = {k: v.id for k, v in objects.items()}

    # delete the area; all other objects should be deleted as well
    db.session.delete(objects["area"])
    db.session.commit()
    deleted_keys = object_ids.keys()
    check_deletions(object_ids, deleted_keys)


def test_delete_sector(test_client_db) -> None:
    """
    When deleting a sector, its routes and their climbs should be deleted. Sessions
    that have no climbs should be deleted as well. The same is true for areas without
    sectors.
    """
    # create the objects and add a second sector, visited in the same session
    objects = create_objects()
    objects["sector_2"] = Sector(name="Test Sector 2", area=objects["area"])
    objects["route_2"] = Route(
        name="Test Route 2", sector=objects["sector_2"], grade_id=1
    )
    objects["climb_2"] = Climb(
        session=objects["session"], route=objects["route_2"], n_attempts=5, sent=True
    )
    object_ids = {k: v.id for k, v in objects.items()}
    db.session.add_all([objects["sector_2"], objects["route_2"], objects["climb_2"]])
    db.session.commit()

    # delete the second sector; the session should remain
    db.session.delete(objects["sector_2"])
    db.session.commit()
    deleted_keys = ["sector_2", "route_2", "climb_2"]
    check_deletions(object_ids, deleted_keys)

    # delete the first sector; nothing should remain
    db.session.delete(objects["sector"])
    db.session.commit()
    check_deletions(object_ids, object_ids.keys())


def test_delete_route(test_client_db) -> None:
    """
    When a route is deleted, all its corresponding climbs should be deleted as well.
    If a sector has no routes left, it should be deleted. The same is true for areas
    with no sectors, and for sessions with no climbs.
    """

    # create the objects and add a second route, visited in the same session
    objects = create_objects()
    objects["route_2"] = Route(
        name="Test Route 2", sector=objects["sector"], grade_id=1
    )
    objects["climb_2"] = Climb(
        session=objects["session"], route=objects["route_2"], n_attempts=5, sent=True
    )
    db.session.add_all([objects["route_2"], objects["climb_2"]])
    db.session.commit()
    object_ids = {k: v.id for k, v in objects.items()}

    # delete the second route; session, area and sector should remain
    db.session.delete(objects["route_2"])
    db.session.commit()
    deleted_keys = ["route_2", "climb_2"]
    check_deletions(object_ids, deleted_keys)

    # delete the first route; session, area and sector should be deleted
    db.session.delete(objects["route"])
    db.session.commit()
    check_deletions(object_ids, object_ids.keys())
