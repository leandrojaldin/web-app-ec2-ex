
from ..models import Reservation, db


def list_reservations(status=None, guest_id=None):
    query = Reservation.query
    if status:
        query = query.filter_by(status=status)
    if guest_id:
        query = query.filter_by(guest_id=guest_id)
    return query.order_by(Reservation.check_in).all()


def get(reservation_id):
    return db.session.get(Reservation, reservation_id)


def create(**fields):
    reservation = Reservation(**fields)
    db.session.add(reservation)
    db.session.commit()
    return reservation


def update(reservation, **fields):
    for name, value in fields.items():
        setattr(reservation, name, value)
    db.session.commit()
    return reservation
