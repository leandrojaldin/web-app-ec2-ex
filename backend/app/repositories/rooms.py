
from ..models import Room, db


def list_rooms(status=None):
    query = Room.query
    if status:
        query = query.filter_by(status=status)
    return query.order_by(Room.number).all()


def get(room_id):
    return db.session.get(Room, room_id)


def find_by_number(number):
    return Room.query.filter_by(number=number).first()


def create(**fields):
    room = Room(**fields)
    db.session.add(room)
    db.session.commit()
    return room


def update(room, **fields):
    for name, value in fields.items():
        setattr(room, name, value)
    db.session.commit()
    return room


def has_reservations(room):
    return bool(room.reservations)


def delete(room):
    db.session.delete(room)
    db.session.commit()
