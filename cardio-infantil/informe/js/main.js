function mostrarAvisos(mensajes, tipo) {
  document.getElementById('listaAvisos').innerHTML =
    mensajes.map(m => `<div class="aviso aviso--${tipo}">${m}</div>`).join('');
}

async function procesarArchivo(file) {
  const anio = Number(document.getElementById('inputAnio').value);
  const mes = Number(document.getElementById('inputMes').value);

  try {
    const wb = await leerArchivo(file);
    const errores = validarColumnas(wb);
    if (errores.length) { mostrarAvisos(errores, 'error'); return; }

    STORE = storeVacio(anio, mes);
    STORE.meta.fuente = file.name;
    cargarConsolidado(wb);

    const c = STORE.indicadores.casos;
    mostrarAvisos([`Archivo "${file.name}" cargado correctamente (${c.alertas} alertas, ${c.requerimientos} requerimientos, ${c.casos_bd} casos de BD).`], 'ok');
    guardarPeriodo();
    renderTodo();
  } catch (err) {
    mostrarAvisos(['No se pudo leer el archivo. Verifica que sea un .csv o .xlsx válido.'], 'error');
    console.error(err);
  }
}

function initUI() {
  const selMes = document.getElementById('inputMes');
  selMes.innerHTML = MESES.map((m, i) => `<option value="${i}">${m}</option>`).join('');

  const dropzone = document.getElementById('dropzone');
  const inputArchivo = document.getElementById('inputArchivo');

  dropzone.addEventListener('click', () => inputArchivo.click());
  inputArchivo.addEventListener('change', e => { if (e.target.files[0]) procesarArchivo(e.target.files[0]); });

  ['dragenter', 'dragover'].forEach(ev =>
    dropzone.addEventListener(ev, e => { e.preventDefault(); dropzone.classList.add('arrastrando'); }));
  ['dragleave', 'drop'].forEach(ev =>
    dropzone.addEventListener(ev, e => { e.preventDefault(); dropzone.classList.remove('arrastrando'); }));
  dropzone.addEventListener('drop', e => { if (e.dataTransfer.files[0]) procesarArchivo(e.dataTransfer.files[0]); });

  document.getElementById('btnAbrirCarga').addEventListener('click', () =>
    document.getElementById('panelCarga').scrollIntoView({ behavior: 'smooth' }));
  document.getElementById('btnExportarPDF').addEventListener('click', exportarPDF);
  document.getElementById('modalCerrar').addEventListener('click', cerrarDetalle);
  document.getElementById('modalFondo').addEventListener('click', e => {
    if (e.target.id === 'modalFondo') cerrarDetalle();
  });

  refrescarListaPeriodosGuardados();
}

window.addEventListener('load', initUI);
