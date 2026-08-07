/* F6 — Novaventa hereda el motor de Acción Fiduciaria, no sus cifras ni su
   inventario contractual. Este archivo contiene solamente datos del cliente. */
window.PERFIL_NOVAVENTA = {
  id: 'novaventa',
  nombre: 'Novaventa',
  celula: 'Célula 3',
  extiende: 'accion-fiduciaria',
  contrato: {codigo: null, inicio: '2025-07-21', vigenciaHasta: '2026-07-20'},
  lineaBase: {
    alcance: 'Administración remota de Bases de datos.',
    estadisticas: [
      {etiqueta: 'Alcance', valor: 'Administración remota', meta: 'Bases de datos'},
      {etiqueta: 'BD SQL Server', valor: '48', meta: 'Bases administradas'},
      {etiqueta: 'BD DB2', valor: '7', meta: 'Bases administradas'},
      {etiqueta: 'Vigencia', valor: '20 jul 2026', meta: 'Contrato vigente', destacada: true},
    ],
  },
  metas: {disponibilidad: 0.99, gestionServicio: 0.90, entregables: 0.80, backups: null},
  tarjetas: {
    // La referencia de junio no tiene bolsa de horas ni una tarjeta separada
    // de mitigaciones. c10 publica capacidad; c12 referencia el anexo Db2.
    seleccionadas: ['c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c10', 'c12'],
    presentacion: {
      c3: {items: [['Línea base'], ['Alcance', 'Admin. remota BD'], ['BD SQL Server', '48'], ['BD DB2', '7'], ['Vigencia', 'Hasta 20/07/2026']], chip: ['ok', 'Vigente']},
      c4: {items: [['Indicadores del servicio'], ['Disponibilidad', '—', 'Meta 99%'], ['Gestión del Servicio', '—', 'Meta 90%'], ['Entregables', '—', 'Meta 80%']]},
      c6: {meta: 'Meta 99% · requiere el consolidado'},
      c7: {meta: 'Requiere la hoja «Backups» · sin meta contractual declarada'},
      c12: {valor: '1 archivo', meta: 'Informe mensual Db2 · junio 2026'},
    },
  },
  fuentes: {
    glpi: {filtroCliente: {campo: 'entidad', estrategia: 'contiene-normalizado', valor: 'novaventa'}},
    alertas: {
      origenes: [
        {id: 'alertops', precedencia: 1, ambito: 'mes-en-curso'},
        {id: 'consolidado-data', precedencia: 2, ambito: 'mes-en-curso'},
      ],
      data: {cabecera: {estrategia: 'primera-fila-con', campos: [['id'], ['categoria'], ['fecha solicitud', 'fechasolicitud']]}, columnas: {id: ['id'], categoria: ['categoria'], fecha: ['fecha solicitud', 'fechasolicitud'], descripcion: ['descripcion', 'descripción']}},
    },
    consolidado: {
      indicadores: {
        hojas: ['Indicadores'],
        cabecera: {estrategia: 'bloque-con-fechas', campos: [['indicador'], ['meta']]},
        metricas: [
          {id: 'disponibilidad', aliases: ['disponibilidad'], rotulo: 'Disponibilidad de la plataforma administrada'},
          {id: 'gestionServicio', aliases: ['cumplimiento tiempos de atencion'], rotulo: 'Gestión del Servicio'},
          {id: 'entregables', aliases: ['cumplimiento de entregables'], rotulo: 'Cumplimiento de entregables'},
        ],
      },
      // La matriz homónima «Disponibilidad» termina en jun-25. El corte
      // vigente se declara por motor en esta tabla (incluye jun-26).
      disponibilidad: {estrategia: 'tabla-con-fechas', hoja: 'Grafica Dispo y Gestion', tabla: 'Disponibilidad Real'},
      capacidad: {hojas: ['Capacidad'], cabecera: {estrategia: 'primera-fila-con', campos: [['cliente'], ['tipo ci']]}},
    },
  },
  textos: {
    tituloDocumento: 'Informe Gerencial · Novaventa', marcaTopbar: 'Informe Novaventa',
    clienteHero: 'NOVAVENTA', confidencialidad: 'Documento confidencial preparado por SETI para Novaventa.',
    nombreArchivo: 'Novaventa',
    carga: {
      consolidadoTitulo: '1. Consolidado mensual Novaventa',
      consolidadoAyuda: 'Carga la plantilla mensual de Novaventa: requiere Indicadores, Disponibilidad, Backups y Capacidad.',
      alertasTitulo: '3. Alertas (AlertsList o Data_<mes>)',
      alertasAyuda: 'Carga Data_<mes>.xlsx aquí; es la fuente alternativa de alertas, no el consolidado de capacidad.',
    },
  },
  almacen: {prefijo: 'informeNovaventa'},
};
