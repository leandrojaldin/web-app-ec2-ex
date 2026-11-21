
from datetime import date

from ..repositories import reservations
from .errors import InvalidInputError, NotFoundError
from .guests import get_guest
from .rooms import get_room


def list_reservations(status=None, guest_id=None):
    return reservations.list_reservations(status, guest_id)


def get_reservation(reservation_id):
    reservation = reservations.get(reservation_id)
    if reservation is None:
        raise NotFoundError("Reserva no encontrada")
    return reservation


def create_reservation(data):
    required = ("room_id", "guest_id", "check_in", "check_out", "guests_count")
    missing = [field for field in required if data.get(field) in (None, "")]
    if missing:
        raise InvalidInputError(f"Faltan campos: {', '.join(missing)}")

    try:
        room_id = int(data["room_id"])
        guest_id = int(data["guest_id"])
    except (TypeError, ValueError, OverflowError):
        raise InvalidInputError("Los identificadores de habitación y huésped deben ser numéricos") from None
    room = get_room(room_id)
    guest = get_guest(guest_id)

    try:
        check_in = date.fromisoformat(data["check_in"])
        check_out = date.fromisoformat(data["check_out"])
        guests_count = int(data["guests_count"])
    except (TypeError, ValueError, OverflowError):
        raise InvalidInputError("Fechas en formato AAAA-MM-DD y guests_count numérico") from None

    nights = (check_out - check_in).days
    return reservations.create(
        room=room, guest=guest, check_in=check_in, check_out=check_out,
        guests_count=guests_count, status="confirmed", total_price=nights * room.price_per_night,
    )


def cancel_reservation(reservation_id):
    reservation = get_reservation(reservation_id)
    return reservations.update(reservation, status="cancelled")


def check_in_reservation(reservation_id):
    reservation = get_reservation(reservation_id)
    return reservations.update(reservation, status="checked_in")


def check_out_reservation(reservation_id):
    reservation = get_reservation(reservation_id)
    return reservations.update(reservation, status="checked_out")
