import * as api from "./api.js";

const ROOM_TYPES = { single: "Simple", double: "Doble", family: "Familiar", suite: "Suite" };
const STATUS_LABELS = {
  available: "Disponible", maintenance: "Mantenimiento",
  confirmed: "Confirmada", checked_in: "Hospedado", checked_out: "Finalizada", cancelled: "Cancelada",
};

// ---------- utilidades ----------
function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

const priceFormat = new Intl.NumberFormat("es-BO", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function showMessage(text, isError) {
  const msg = document.getElementById("msg");
  msg.textContent = text;
  msg.className = isError ? "message message--error" : "message";
  msg.hidden = false;
  clearTimeout(showMessage.timer);
  if (!isError) showMessage.timer = setTimeout(() => { msg.hidden = true; }, 4000);
}

// ---------- pestañas ----------
document.querySelectorAll("[data-tab]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-tab]").forEach((b) => b.classList.remove("tabs__button--active"));
    button.classList.add("tabs__button--active");
    document.querySelectorAll("[data-panel]").forEach((tab) => { tab.hidden = true; });
    document.getElementById("tab-" + button.dataset.tab).hidden = false;
  });
});

// ---------- habitaciones ----------
async function loadRooms() {
  try {
    const rooms = await api.listRooms();
    const body = document.getElementById("rooms-body");
    if (rooms.length === 0) {
      body.innerHTML = '<tr><td colspan="6" class="table__cell table__cell--empty">No hay habitaciones</td></tr>';
    } else {
      body.innerHTML = rooms.map((r) => `
        <tr>
          <td class="table__cell">${esc(r.number)}</td>
          <td class="table__cell">${esc(ROOM_TYPES[r.type] || r.type)}</td>
          <td class="table__cell">Bs ${esc(r.price_per_night)}</td>
          <td class="table__cell">${esc(r.capacity)}</td>
          <td class="table__cell"><span class="badge badge--${esc(r.status).replaceAll("_", "-")}">${esc(STATUS_LABELS[r.status])}</span></td>
          <td class="table__cell">
            <button class="table__action button button--small button--secondary" data-action="maintenance" data-id="${esc(r.id)}" data-status="${esc(r.status)}">
              ${r.status === "maintenance" ? "Habilitar" : "Mantenimiento"}
            </button>
            <button class="table__action button button--small button--danger" data-action="delete-room" data-id="${esc(r.id)}">Eliminar</button>
          </td>
        </tr>`).join("");
    }
    // también llena el select del formulario de reservas
    document.getElementById("reservation-room").innerHTML = rooms
      .map((r) => `<option value="${esc(r.id)}">${esc(r.number)} · ${esc(ROOM_TYPES[r.type])} · Bs ${esc(r.price_per_night)}</option>`)
      .join("");
  } catch (error) {
    showMessage(error.message, true);
  }
}

document.getElementById("room-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  runAction(async () => {
    const data = Object.fromEntries(new FormData(form));
    data.price_per_night = Number(data.price_per_night);
    data.capacity = Number(data.capacity);

    const body = await api.createRoom(data);
    form.reset();
    showMessage("Habitación " + body.number + " creada");
    loadRooms();
  });
});

async function toggleMaintenance(id, status) {
  await api.updateRoom(id, { status: status === "maintenance" ? "available" : "maintenance" });
  loadRooms();
}

async function deleteRoom(id) {
  if (!confirm("¿Eliminar la habitación?")) return;
  await api.deleteRoom(id);
  showMessage("Habitación eliminada");
  loadRooms();
}

// ---------- huéspedes ----------
async function loadGuests() {
  try {
    const guests = await api.listGuests();
    const body = document.getElementById("guests-body");
    if (guests.length === 0) {
      body.innerHTML = '<tr><td colspan="4" class="table__cell table__cell--empty">No hay huéspedes</td></tr>';
    } else {
      body.innerHTML = guests.map((g) => `
        <tr>
          <td class="table__cell">${esc(g.full_name)}</td>
          <td class="table__cell">${esc(g.email)}</td>
          <td class="table__cell">${esc(g.document)}</td>
          <td class="table__cell"><button class="table__action button button--small button--danger" data-action="delete-guest" data-id="${esc(g.id)}">Eliminar</button></td>
        </tr>`).join("");
    }
    document.getElementById("reservation-guest").innerHTML = guests
      .map((g) => `<option value="${esc(g.id)}">${esc(g.full_name)}</option>`)
      .join("");
  } catch (error) {
    showMessage(error.message, true);
  }
}

document.getElementById("guest-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  runAction(async () => {
    const data = Object.fromEntries(new FormData(form));

    const body = await api.createGuest(data);
    form.reset();
    showMessage("Huésped " + body.full_name + " registrado");
    loadGuests();
  });
});

async function deleteGuest(id) {
  if (!confirm("¿Eliminar el huésped?")) return;
  await api.deleteGuest(id);
  showMessage("Huésped eliminado");
  loadGuests();
}

// ---------- reservas ----------
async function loadReservations() {
  try {
    const status = document.getElementById("reservation-filter").value;
    const reservations = await api.listReservations(status);
    const body = document.getElementById("reservations-body");
    if (reservations.length === 0) {
      body.innerHTML = '<tr><td colspan="10" class="table__cell table__cell--empty">No hay reservas</td></tr>';
      return;
    }
    body.innerHTML = reservations.map((r) => `
      <tr>
        <td class="table__cell">${esc(r.id)}</td>
        <td class="table__cell">${esc(r.room_number)}</td>
        <td class="table__cell">${esc(r.guest_name)}</td>
        <td class="table__cell">${esc(r.check_in)}</td>
        <td class="table__cell">${esc(r.check_out)}</td>
        <td class="table__cell">${esc(r.nights)}</td>
        <td class="table__cell">${esc(r.guests_count)}</td>
        <td class="table__cell">${priceFormat.format(r.total_price)}</td>
        <td class="table__cell"><span class="badge badge--${esc(r.status).replaceAll("_", "-")}">${esc(STATUS_LABELS[r.status])}</span></td>
        <td class="table__cell">
          <button class="table__action button button--small button--success" data-action="check-in" data-id="${esc(r.id)}">Check-in</button>
          <button class="table__action button button--small" data-action="check-out" data-id="${esc(r.id)}">Check-out</button>
          <button class="table__action button button--small button--danger" data-action="cancel" data-id="${esc(r.id)}">Cancelar</button>
        </td>
      </tr>`).join("");
  } catch (error) {
    showMessage(error.message, true);
  }
}

document.getElementById("reservation-filter").addEventListener("change", loadReservations);

document.getElementById("reservation-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  runAction(async () => {
    const data = Object.fromEntries(new FormData(form));
    data.room_id = Number(data.room_id);
    data.guest_id = Number(data.guest_id);
    data.guests_count = Number(data.guests_count);

    const body = await api.createReservation(data);
    form.reset();
    showMessage("Reserva #" + body.id + " creada · total Bs " + priceFormat.format(body.total_price));
    loadReservations();
  });
});

async function changeReservation(id, operation) {
  const body = await operation(id);
  showMessage("Reserva #" + id + ": " + STATUS_LABELS[body.status] + " · total Bs " + priceFormat.format(body.total_price));
  await loadReservations();
}

async function runAction(action) {
  try {
    await action();
  } catch (error) {
    showMessage(error.message, true);
  }
}

const actions = {
  maintenance: ({ id, status }) => toggleMaintenance(id, status),
  "delete-room": ({ id }) => deleteRoom(id),
  "delete-guest": ({ id }) => deleteGuest(id),
  "check-in": ({ id }) => changeReservation(id, api.checkInReservation),
  "check-out": ({ id }) => changeReservation(id, api.checkOutReservation),
  cancel: ({ id }) => changeReservation(id, api.cancelReservation),
};

document.querySelector("main").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (button) runAction(() => actions[button.dataset.action](button.dataset));
});

// ---------- inicio ----------
loadRooms();
loadGuests();
loadReservations();
