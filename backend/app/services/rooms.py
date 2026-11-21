
from ..repositories import rooms
from .errors import ConflictError, InvalidInputError, NotFoundError

ROOM_TYPES = ("single", "double", "family", "suite")
ROOM_STATUSES = ("available", "maintenance")


def list_rooms(status=None):
    return rooms.list_rooms(status)


def get_room(room_id):
    room = rooms.get(room_id)
    if room is None:
        raise NotFoundError("Habitación no encontrada")
    return room


def _validate_type(room_type):
    if room_type not in ROOM_TYPES:
        raise InvalidInputError(f"Tipo inválido. Usa: {', '.join(ROOM_TYPES)}")


def _numeric_fields(data):
    fields = {}
    try:
        if "price_per_night" in data:
            fields["price_per_night"] = float(data["price_per_night"])
        if "capacity" in data:
            fields["capacity"] = int(data["capacity"])
    except (TypeError, ValueError, OverflowError):
        raise InvalidInputError("price_per_night y capacity deben ser números") from None
    return fields


def create_room(data):
    required = ("number", "type", "price_per_night", "capacity")
    missing = [field for field in required if data.get(field) in (None, "")]
    if missing:
        raise InvalidInputError(f"Faltan campos: {', '.join(missing)}")

    _validate_type(data["type"])
    fields = _numeric_fields(data)
    number = str(data["number"]).strip()
    if rooms.find_by_number(number):
        raise ConflictError("Ya existe una habitación con ese número")
    return rooms.create(number=number, type=data["type"], status=data.get("status", "available"), **fields)


def update_room(room_id, data):
    room = get_room(room_id)
    changes = {}
    if "type" in data:
        _validate_type(data["type"])
        changes["type"] = data["type"]
    if "status" in data:
        if data["status"] not in ROOM_STATUSES:
            raise InvalidInputError(f"Estado inválido. Usa: {', '.join(ROOM_STATUSES)}")
        changes["status"] = data["status"]
    changes.update(_numeric_fields(data))
    return rooms.update(room, **changes)


def delete_room(room_id):
    room = get_room(room_id)
    if rooms.has_reservations(room):
        raise ConflictError("La habitación tiene reservas registradas")
    rooms.delete(room)
