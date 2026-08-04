const LS_PREFIJO = 'informe-gerencial:';

function claveDePeriodo(anio, mes) {
  return `${LS_PREFIJO}${anio}-${String(mes + 1).padStart(2, '0')}`;
}

function guardarPeriodo() {
  if (!STORE) return;
  const clave = claveDePeriodo(STORE.periodo.anio, STORE.periodo.mes);
  localStorage.setItem(clave, JSON.stringify(STORE));
  refrescarListaPeriodosGuardados();
}

function listarPeriodosGuardados() {
  return Object.keys(localStorage).filter(k => k.startsWith(LS_PREFIJO)).sort().reverse();
}

function cargarPeriodoGuardado(clave) {
  const crudo = localStorage.getItem(clave);
  if (!crudo) return;
  STORE = JSON.parse(crudo);
  renderTodo();
}

function borrarPeriodoGuardado(clave) {
  localStorage.removeItem(clave);
  refrescarListaPeriodosGuardados();
}

function refrescarListaPeriodosGuardados() {
  const cont = document.getElementById('chipsPeriodos');
  const claves = listarPeriodosGuardados();
  if (!claves.length) {
    cont.innerHTML = '<span class="vacio">Ninguno todavía.</span>';
    return;
  }
  cont.innerHTML = claves.map(clave => `
    <span class="chip-periodo" data-clave="${clave}">
      <span class="chip-periodo__abrir">${clave.replace(LS_PREFIJO, '')}</span>
      <button class="chip-periodo__borrar" title="Borrar">✕</button>
    </span>`).join('');

  cont.querySelectorAll('.chip-periodo__abrir').forEach(el =>
    el.addEventListener('click', () => cargarPeriodoGuardado(el.closest('.chip-periodo').dataset.clave)));

  cont.querySelectorAll('.chip-periodo__borrar').forEach(el =>
    el.addEventListener('click', e => {
      e.stopPropagation();
      borrarPeriodoGuardado(el.closest('.chip-periodo').dataset.clave);
    }));
}
