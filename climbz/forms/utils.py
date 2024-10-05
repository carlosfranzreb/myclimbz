def format_name(name: str) -> str:
    """
    Return the name in the correct format: stripped of whitespace and as a title.
    This function is used to format the names of areas, sectors, and routes.
    """
    return name.strip().lower().title()
