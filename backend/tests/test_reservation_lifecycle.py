
from datetime import datetime, timedelta

import pytest

from app.services import reservations


@pytest.fixture
def hotel_clock(monkeypatch):
    now = datetime(2030, 6, 15, 12, tzinfo=reservations.HOTEL_TIMEZONE)
    monkeypatch.setattr(reservations, "hotel_now", lambda: now)
    return now


def make_reservation(client, room, guest, arrival):
    return client.post("/api/reservations", json={
        "room_id": room["id"],
        "guest_id": guest["id"],
        "check_in": arrival.isoformat(),
        "check_out": (arrival + timedelta(days=1)).isoformat(),
        "guests_count": 1,
    })


@pytest.mark.parametrize("prior_action, invalid_action", [
    (None, "check-out"),
    ("cancel", "check-in"),
    ("check-in", "cancel"),
])
def test_invalid_state_transition_is_rejected(client, room, guest, hotel_clock, prior_action, invalid_action):
    created = make_reservation(client, room, guest, hotel_clock.date())
    assert created.status_code == 201
    path = f"/api/reservations/{created.get_json()['id']}"
    if prior_action is not None:
        assert client.patch(f"{path}/{prior_action}").status_code == 200
    response = client.patch(f"{path}/{invalid_action}")
    assert response.status_code == 422
    assert response.get_json() == {"error": "No se permite esta acción para el estado de la reserva"}


def test_check_in_cannot_happen_before_arrival(client, room, guest, hotel_clock):
    created = make_reservation(client, room, guest, hotel_clock.date() + timedelta(days=1))
    assert created.status_code == 201
    reservation_id = created.get_json()["id"]
    response = client.patch(f"/api/reservations/{reservation_id}/check-in")
    assert response.status_code == 422
    assert response.get_json() == {"error": "El check-in no puede realizarse antes de la fecha de ingreso"}


def test_guest_can_have_at_most_three_active_reservations(client, room, guest, hotel_clock):
    today = hotel_clock.date()
    first = make_reservation(client, room, guest, today)
    assert first.status_code == 201
    first_path = f"/api/reservations/{first.get_json()['id']}"
    assert client.patch(f"{first_path}/check-in").status_code == 200
    for days in (2, 4):
        assert make_reservation(client, room, guest, today + timedelta(days=days)).status_code == 201

    fourth_date = today + timedelta(days=6)
    response = make_reservation(client, room, guest, fourth_date)
    assert response.status_code == 422
    assert response.get_json() == {"error": "El huésped ya tiene 3 reservas activas"}

    assert client.patch(f"{first_path}/check-out").status_code == 200
    assert make_reservation(client, room, guest, fourth_date).status_code == 201
