
from . import db


class ReservationRate(db.Model):
    """Tarifa original de la reserva, independiente de cambios en la habitación."""

    __tablename__ = "reservation_rates"

    reservation_id = db.Column(db.Integer, db.ForeignKey("reservations.id"), primary_key=True)
    price_per_night = db.Column(db.Float, nullable=False)

    reservation = db.relationship("Reservation")
