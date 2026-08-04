function exportarHTML() {
  const copia = document.documentElement.cloneNode(true);
  copia.querySelectorAll('script[src^="js/"]').forEach(s => s.remove());
  copia.querySelector('.carga-panel')?.remove();

  const blob = new Blob(['<!DOCTYPE html>\n' + copia.outerHTML], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `informe-${STORE.periodo.anio}-${String(STORE.periodo.mes + 1).padStart(2, '0')}.html`;
  a.click();
  URL.revokeObjectURL(url);
}