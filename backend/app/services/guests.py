
from ..repositories import guests
from .errors import ConflictError, InvalidInputError, NotFoundError


def list_guests():
    return guests.list_guests()


def get_guest(guest_id):
    guest = guests.get(guest_id)
    if guest is None:
        raise NotFoundError("Huésped no encontrado")
    return guest


def create_guest(data):
    required = ("full_name", "email", "document")
    missing = [field for field in required if not str(data.get(field) or "").strip()]
    if missing:
        raise InvalidInputError(f"Faltan campos: {', '.join(missing)}")
    if not isinstance(data["full_name"], str) or not isinstance(data["email"], str):
        raise InvalidInputError("Nombre y email deben ser texto")

    email = data["email"].strip().lower()
    if "@" not in email:
        raise InvalidInputError("Email inválido")
    if guests.find_by_email(email):
        raise ConflictError("Ya existe un huésped con ese email")

    return guests.create(full_name=data["full_name"].strip(), email=email, document=str(data["document"]).strip())


def delete_guest(guest_id):
    guest = get_guest(guest_id)
    if guests.has_reservations(guest):
        raise ConflictError("El huésped tiene reservas registradas")
    guests.delete(guest)
