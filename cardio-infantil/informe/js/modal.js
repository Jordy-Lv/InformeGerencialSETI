let chartActivo = null;

function abrirDetalle(id) {
  const def = DEFINICION_TARJETAS.find(d => d.id === id);
  if (!def) return;

  document.getElementById('modalTitulo').textContent = def.titulo;
  document.getElementById('modalNarrativa').textContent = def.narrativa(STORE);
  document.getElementById('modalFondo').classList.add('abierto');

  if (chartActivo) chartActivo.destroy();
  chartActivo = new Chart(document.getElementById('modalCanvas'), def.grafico(STORE));
}

function cerrarDetalle() {
  document.getElementById('modalFondo').classList.remove('abierto');
  if (chartActivo) { chartActivo.destroy(); chartActivo = null; }
}
