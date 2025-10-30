const API = 'http://localhost:5000';
async function loadRanking(){
  try{
    const res = await fetch(API + '/ranking');
    const data = await res.json();
    const ol = document.getElementById('listaRanking');
    if(Array.isArray(data)){
      ol.innerHTML = data.map(u => `<li>${u.nombre || ('ID '+u.usuarioid)} — ${u.points} pts</li>`).join('');
    } else {
      ol.innerHTML = '<li>No hay datos de ranking.</li>';
    }
  }catch(e){
    console.error(e);
  }
}
async function loadRecientes(){
  try{
    const res = await fetch(API + '/reciclaje');
    const data = await res.json();
    const ul = document.getElementById('listaRecientes');
    if(Array.isArray(data)){
      ul.innerHTML = data.slice(0,20).map(r => `<li>${r.material} — ${r.cantidad}kg — usuario ${r.usuarioid} — ${r.fecha}</li>`).join('');
    } else {
      ul.innerHTML = '<li>No hay registros.</li>';
    }
  }catch(e){ console.error(e); }
}
document.getElementById('formReciclar').addEventListener('submit', async (ev)=>{
  ev.preventDefault();
  const usuarioid = Number(document.getElementById('usuarioid').value);
  const material = document.getElementById('material').value;
  const cantidad = Number(document.getElementById('cantidad').value);
  const payload = { usuarioid, material, cantidad };
  try{
    const res = await fetch(API + '/reciclaje', {
      method:'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if(data.ok){
      document.getElementById('mensaje').innerText = 'Registrado! Puntos: ' + data.points;
      loadRanking();
      loadRecientes();
    } else {
      document.getElementById('mensaje').innerText = 'Error: ' + (data.error || JSON.stringify(data));
    }
  }catch(e){
    document.getElementById('mensaje').innerText = 'Error al conectar con backend.';
    console.error(e);
  }
});
// initial load
loadRanking();
loadRecientes();
