/* Perfil de cliente: Acción Fiduciaria. Datos puros — sin funciones (ver
   openspec/project.md, "Multicliente por configuración, no por copia").
   F1 extrae este perfil del HTML donde vivía disperso (48+ literales
   repetidos en 6 puntos de comparación distintos, más los textos de la
   interfaz) — ver docs/2026-08-04-f1-perfil-accion-fiduciaria.md para el
   detalle de dónde vivía cada dato antes de este cambio. */
window.PERFIL_ACCION_FIDUCIARIA = {
  id: 'accion-fiduciaria',
  nombre: 'Acción Fiduciaria',
  celula: 'Célula 3',
  extiende: null,

  contrato: {
    codigo: 'CN-21012025',
    vigenciaHasta: '2026-08-31',
  },

  metas: {
    disponibilidad: 0.9930,
    gestionServicio: 0.95,
    entregables: 0.90,
  },

  // Alias que también identifican a este cliente dentro de una columna de
  // "Cliente"/"Entidad" de un archivo cargado, además del nombre completo
  // normalizado. Existía ya como caso especial en esClienteAccion() (línea
  // ~3431 del HTML, antes de este cambio) — se conserva tal cual, no se
  // inventa un alias nuevo.
  aliasCliente: ['accion'],

  almacen: {
    // Prefijo de las claves en localStorage/IndexedDB. Las claves viejas
    // ('informeAF', 'informeAF:posiciones', 'informeAF:bolsa:') se siguen
    // leyendo — ver claveAlmacen() y su migración de solo lectura.
    prefijo: 'informeAF',
  },

  textos: {
    tituloDocumento: 'Informe Gerencial · Acción Fiduciaria',
    marcaTopbar: 'Informe Acción Fiduciaria',
    clienteHero: 'ACCIÓN FIDUCIARIA',
    confidencialidad: 'Documento confidencial preparado por SETI para Acción Fiduciaria.',
  },
};
