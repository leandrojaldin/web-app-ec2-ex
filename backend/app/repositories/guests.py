
from ..models import Guest, db


def list_guests():
    return Guest.query.order_by(Guest.full_name).all()


def get(guest_id):
    return db.session.get(Guest, guest_id)


def find_by_email(email):
    return Guest.query.filter_by(email=email).first()


def create(**fields):
    guest = Guest(**fields)
    db.session.add(guest)
    db.session.commit()
    return guest


def has_reservations(guest):
    return bool(guest.reservations)


def delete(guest):
    db.session.delete(guest)
    db.session.commit()
