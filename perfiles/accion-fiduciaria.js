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
    // Fecha calendario ISO. F2 la valida al arrancar y es la fuente de
    // verdad para los históricos; el DOM solo la presenta como 01/09/2025.
    inicio: '2025-09-01',
    vigenciaHasta: '2026-08-31',
  },

  metas: {
    disponibilidad: 0.9930,
    gestionServicio: 0.95,
    entregables: 0.90,
  },

  // F3: orden entregado de las tarjetas. Son ids de inventario, no selectores
  // ni funciones; F4 añadirá los operadores de herencia y el preset editable.
  tarjetas: {
    seleccionadas: ['c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c8m', 'c9', 'c11', 'c12'],
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
    // Sin tilde a propósito: nombre de archivo (PDF/HTML exportado). El
    // nombre original ya se generaba así (probablemente por seguridad de
    // nombre de archivo entre sistemas) — se conserva ese valor exacto,
    // no se deriva de `nombre` para no cambiar el nombre del entregable.
    nombreArchivo: 'Accion Fiduciaria',
  },
};
