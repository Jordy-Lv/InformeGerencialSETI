function renderTodo() {
  document.getElementById('periodoActualLabel').textContent = `${MESES[STORE.periodo.mes]} ${STORE.periodo.anio}`;
  document.getElementById('btnExportarPDF').disabled = false;
  renderDeck();
}

function renderDeck() {
  const deck = document.getElementById('deck');
  deck.innerHTML = `
    <div class="stage-wrap"><div class="slide slide--portada">
      <div class="portada-texto">
        <img class="logo-portada" src="assets/logo-seti.png" alt="Logo" />
        <h1>Informe<br>Gerencial</h1>
        <p class="cliente">CLIENTE: ${CONFIG.clienteNombre.toUpperCase()}</p>
        <div class="periodo-box">
          <span class="icono">
            <svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2" fill="none" stroke-width="1.7"/><path d="M3 10h18M8 3v4M16 3v4" stroke-width="1.7"/></svg>
          </span>
          <div>
            <small>Periodo del informe</small>
            <strong>${MESES[STORE.periodo.mes][0].toUpperCase()}${MESES[STORE.periodo.mes].slice(1)} ${STORE.periodo.anio}</strong>
          </div>
        </div>
      </div>
      <div class="mosaico">
        <div class="span-2">Foto equipo</div>
        <div class="acento"></div>
        <div>Foto equipo</div>
        <div>Foto equipo</div>
        <div class="fila-2">Foto equipo</div>
        <div>Foto equipo</div>
        <div>Foto equipo</div>
        <div>Foto equipo</div>
        <div>Foto equipo</div>
        <div class="acento"></div>
        <div>Foto equipo</div>
      </div>
    </div></div>

    <div class="franja-colores"></div>

    <div class="seccion-header">
      <span class="num">01</span>
      <h2>Marco contractual</h2>
    </div>

    <div class="stage-wrap"><div class="slide">
      <div class="slide__kicker">02 · Operación del período</div>
      <h2 class="slide__titulo">Resumen de indicadores</h2>
      <div class="tarjetas" id="grillaTarjetas"></div>
    </div></div>
  `;

  const grilla = document.getElementById('grillaTarjetas');
  grilla.innerHTML = DEFINICION_TARJETAS.map(def => {
    const v = def.valor(STORE);
    const estado = def.estado(STORE);
    const sinDato = estado === 'sin-dato';
    return `
      <div class="tarjeta ${sinDato ? 'tarjeta--sin-dato' : 'tarjeta--' + estado}" data-id="${def.id}">
        <small>${def.titulo}</small>
        <strong>${sinDato ? '—' : (v ?? '—') + def.unidad}</strong>
        <span class="meta">${sinDato ? 'Sin dato para este período' : 'Ver detalle'}</span>
      </div>`;
  }).join('');

  grilla.querySelectorAll('.tarjeta:not(.tarjeta--sin-dato)').forEach(el =>
    el.addEventListener('click', () => abrirDetalle(el.dataset.id)));

  ajustarEscalaSlides();
}

// css/styles.css define `.slide{width:1280px;height:720px}` (lienzo fijo,
// como una diapositiva) y una regla @media(max-width:1360px) que aplica
// `transform:scale(var(--escala,1))` — pero nada calculaba nunca esa
// variable, así que en cualquier pantalla angosta (una laptop normal,
// <1280px) el informe se desbordaba con scroll horizontal en vez de
// encogerse. Esta función calcula la escala real y también fija el alto en
// px del contenedor (el transform no libera el espacio de layout por sí
// solo, así que sin esto quedaría un hueco en blanco del tamaño original
// debajo de cada diapositiva encogida).
function ajustarEscalaSlides() {
  const disponible = document.documentElement.clientWidth - 32;
  const escala = Math.min(1, disponible / 1280);
  document.querySelectorAll('.stage-wrap').forEach(wrap => {
    wrap.style.setProperty('--escala', escala);
    wrap.style.height = (720 * escala) + 'px';
  });
}

window.addEventListener('resize', ajustarEscalaSlides);