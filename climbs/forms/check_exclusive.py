from climbs import db


def check_exclusivity(field_model: db.Model, new: str, existing: str) -> str:
    """
    - If no existing field was chosen, ensure that the name of a new one was given.
    - Ensure that the new field is not already in the database.

    Args:
        field_model (db.Model): model of the field, e.g. Area. Used to query the
            database for existing fields and to generate the error message.
        new (str): value of the new field, a string field in the form.
        existing (str): value of the existing field, a select field in the form where
            whose selected option has the ID given here. ID=0 means no option was
            selected.

    Returns:
        str: error message if the fields are not mutually exclusive, otherwise None.
    """

    field_name = field_model.__name__
    has_new = new is not None
    if has_new is True:
        has_new = len(new) > 0
    has_existing = existing is not None
    if has_existing is True:
        has_existing = existing != "0"

    if not (has_new or has_existing):
        return f"{field_name} is required"
    elif has_new:
        if field_model.query.filter_by(name=new).first() is not None:
            return f"{field_name} {new} already exists"
