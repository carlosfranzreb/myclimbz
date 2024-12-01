"""
Custom columns for SQLAlchemy models
"""

from sqlalchemy import Column, Integer, CheckConstraint


class ConstrainedInteger(Column):
    """An integer column with a check constraint."""

    def __init__(self, name: str, min_value: int, max_value: int, **kwargs):
        super().__init__(
            Integer,
            CheckConstraint(f"{name} >= {min_value} and {name} <= {max_value}"),
            nullable=True,
            **kwargs,
        )


class Rating(ConstrainedInteger):
    """A column for ratings."""

    def __init__(self, name: str, **kwargs):
        super().__init__(name, 0, 5, **kwargs)
