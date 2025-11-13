const API = "http://localhost:5000";

async function loadRanking() {
  const res = await fetch(API + "/ranking");
  const data = await res.json();
  const list = document.getElementById("listaRanking");

  list.innerHTML = data
    .map(u => `<li>${u.nombre || "Usuario " + u.usuarioid} — ${u.points} pts</li>`)
    .join("");
}

async function loadRecientes() {
  const res = await fetch(API + "/reciclaje");
  const data = await res.json();
  const list = document.getElementById("listaRecientes");

  list.innerHTML = data
    .slice(0, 20)
    .map(r => `<li>${r.material} — ${r.cantidad}kg — Usuario ${r.usuarioid}</li>`)
    .join("");
}

document.getElementById("formReciclar").addEventListener("submit", async e => {
  e.preventDefault();

  const payload = {
    usuarioid: Number(document.getElementById("usuarioid").value),
    material: document.getElementById("material").value,
    cantidad: Number(document.getElementById("cantidad").value)
  };

  const res = await fetch(API + "/reciclaje", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  if (data.ok) {
    document.getElementById("mensaje").innerText = "Registrado ✔️ Puntos: " + data.points;
    loadRanking();
    loadRecientes();
  }
});

loadRanking();
loadRecientes();

