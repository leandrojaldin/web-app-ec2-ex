
from contextlib import contextmanager

from sqlalchemy import text

from ..models import Reservation, db


@contextmanager
def transaction():
    # SQLite toma el bloqueo de escritura antes de leer el estado de la reserva.
    # Así, dos altas simultáneas no pueden validar las mismas fechas libres.
    try:
        if db.engine.dialect.name == "sqlite":
            db.session.execute(text("BEGIN IMMEDIATE"))
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def list_reservations(status=None, guest_id=None):
    query = Reservation.query
    if status:
        query = query.filter_by(status=status)
    if guest_id:
        query = query.filter_by(guest_id=guest_id)
    return query.order_by(Reservation.check_in).all()


def get(reservation_id):
    return db.session.get(Reservation, reservation_id)


def has_overlap(room_id, check_in, check_out, statuses):
    return Reservation.query.filter(
        Reservation.room_id == room_id,
        Reservation.status.in_(statuses),
        Reservation.check_in < check_out,
        Reservation.check_out > check_in,
    ).first() is not None


def count_by_guest_and_status(guest_id, statuses):
    return Reservation.query.filter(
        Reservation.guest_id == guest_id,
        Reservation.status.in_(statuses),
    ).count()


def create(**fields):
    reservation = Reservation(**fields)
    db.session.add(reservation)
    return reservation


def update(reservation, **fields):
    for name, value in fields.items():
        setattr(reservation, name, value)
    return reservation
