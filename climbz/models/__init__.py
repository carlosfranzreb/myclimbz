"""
Gathers all the models in the climbs app. They are sorted by their dependencies, so that
the models that depend on others are imported after the models they depend on.
"""

from climbz.models.predictions import Predictions  # noqa: F401
from climbz.models.rock_type import RockType  # noqa: F401
from climbz.models.grade import Grade  # noqa: F401
from climbz.models.crux import Crux  # noqa: F401
from climbz.models.climb import Climb  # noqa: F401
from climbz.models.route import Route  # noqa: F401
from climbz.models.sector import Sector  # noqa: F401
from climbz.models.area import Area  # noqa: F401
from climbz.models.session import Session  # noqa: F401
