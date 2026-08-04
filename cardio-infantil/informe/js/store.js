let STORE = null;

function storeVacio(anio, mes) {
  return {
    periodo: { anio, mes },
    indicadores: {
      // Sin "incidentes": el consolidado de Cardio Infantil no separa esa
      // categoría como Acción Fiduciaria — separa alertas, requerimientos
      // de sistema operativo y casos de base de datos (hoja propia, ver
      // docs/2026-08-03-inventario-tarjetas-cardio-infantil.md).
      casos: { alertas: 0, requerimientos: 0, casos_bd: 0, historico: [] },
      disponibilidad: { porcentaje: null, detalle: [] },
      bolsaHoras: { asignadas: 0, consumidas: 0, saldo: 0 }
    },
    cualitativo: { logros: [], mitigaciones: [] },
    meta: { fuente: '', avisos: [], errores: [] }
  };
}
