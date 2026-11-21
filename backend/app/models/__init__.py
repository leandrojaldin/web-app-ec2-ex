from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .room import Room  # noqa: E402
from .guest import Guest  # noqa: E402
from .reservation import Reservation  # noqa: E402
from .reservation_rate import ReservationRate  # noqa: E402

__all__ = ["db", "Room", "Guest", "Reservation", "ReservationRate"]
