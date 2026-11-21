
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from ..repositories import reservations
from .errors import BusinessRuleError, InvalidInputError, NotFoundError
from .guests import get_guest
from .rooms import get_room

HOTEL_TIMEZONE = timezone(timedelta(hours=-4))
ACTIVE_STATUSES = ("confirmed", "checked_in")
MAX_ACTIVE_RESERVATIONS = 3
MIN_DISCOUNT_NIGHTS = 7
LONG_STAY_DISCOUNT = Decimal("0.10")


def hotel_now():
    return datetime.now(HOTEL_TIMEZONE)


def list_reservations(status=None, guest_id=None):
    return reservations.list_reservations(status, guest_id)


def get_reservation(reservation_id):
    reservation = reservations.get(reservation_id)
    if reservation is None:
        raise NotFoundError("Reserva no encontrada")
    return reservation


def _calculate_total(price_per_night, nights):
    total = Decimal(str(price_per_night)) * nights
    if nights >= MIN_DISCOUNT_NIGHTS:
        total *= 1 - LONG_STAY_DISCOUNT
    return float(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


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

    with reservations.transaction():
        room = get_room(room_id)
        guest = get_guest(guest_id)

        try:
            check_in = date.fromisoformat(data["check_in"])
            check_out = date.fromisoformat(data["check_out"])
            guests_count = int(data["guests_count"])
        except (TypeError, ValueError, OverflowError):
            raise InvalidInputError("Fechas en formato AAAA-MM-DD y guests_count numérico") from None

        if check_out <= check_in:
            raise BusinessRuleError("La fecha de salida debe ser posterior a la de ingreso")
        if check_in < hotel_now().date():
            raise BusinessRuleError("La fecha de ingreso no puede estar en el pasado")
        raw_count = data["guests_count"]
        if isinstance(raw_count, bool) or isinstance(raw_count, float) and not raw_count.is_integer():
            raise BusinessRuleError("La cantidad de huéspedes debe ser un número entero")
        if not 1 <= guests_count <= room.capacity:
            raise BusinessRuleError(f"La cantidad de huéspedes debe estar entre 1 y {room.capacity}")
        if room.status == "maintenance":
            raise BusinessRuleError("La habitación está en mantenimiento")
        if reservations.has_overlap(room_id, check_in, check_out, ACTIVE_STATUSES):
            raise BusinessRuleError("La habitación ya está reservada en esas fechas")
        if reservations.count_by_guest_and_status(guest_id, ACTIVE_STATUSES) >= MAX_ACTIVE_RESERVATIONS:
            raise BusinessRuleError(f"El huésped ya tiene {MAX_ACTIVE_RESERVATIONS} reservas activas")

        nights = (check_out - check_in).days
        return reservations.create(
            room=room, guest=guest, check_in=check_in, check_out=check_out,
            guests_count=guests_count, status="confirmed",
            total_price=_calculate_total(room.price_per_night, nights),
        )


def _require_state(reservation, expected_status):
    if reservation.status != expected_status:
        raise BusinessRuleError("No se permite esta acción para el estado de la reserva")


def cancel_reservation(reservation_id):
    with reservations.transaction():
        reservation = get_reservation(reservation_id)
        _require_state(reservation, "confirmed")
        return reservations.update(reservation, status="cancelled")


def check_in_reservation(reservation_id):
    with reservations.transaction():
        reservation = get_reservation(reservation_id)
        _require_state(reservation, "confirmed")
        if hotel_now().date() < reservation.check_in:
            raise BusinessRuleError("El check-in no puede realizarse antes de la fecha de ingreso")
        return reservations.update(reservation, status="checked_in")


def check_out_reservation(reservation_id):
    with reservations.transaction():
        reservation = get_reservation(reservation_id)
        _require_state(reservation, "checked_in")
        return reservations.update(reservation, status="checked_out")
