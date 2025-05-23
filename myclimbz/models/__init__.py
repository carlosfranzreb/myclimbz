"""
Gathers all the models in the climbs app. They are sorted by their dependencies, so that
the models that depend on others are imported after the models they depend on.
"""

from .video import Video, VideoAttempt  # noqa
from .rock_type import RockType  # noqa
from .grade import Grade  # noqa
from .crux import Crux  # noqa
from .opinion import Opinion  # noqa
from .climb import Climb  # noqa
from .route import Route  # noqa
from .sector import Sector  # noqa
from .area import Area  # noqa
from .session import Session  # noqa
from .climber import Climber  # noqa
