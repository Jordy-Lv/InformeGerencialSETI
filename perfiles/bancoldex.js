/* F7 — Perfil de cliente: Bancóldex. Datos puros — sin funciones (ver
   openspec/project.md). Extiende 'base', no 'accion-fiduciaria': el delta de
   estructuras (fuente de casos, esquema de columnas, 4 indicadores en vez de
   3, disponibilidad por motor, backups por BD) supera el 30% de claves hoja
   permitido para heredar de un perfil de cliente — ver
   docs/2026-08-04-plan-multicliente.md y el reconocimiento en
   docs/2026-08-05-reconocimiento-bancoldex.md.

   contrato, lineaBase y metas vienen de Bancoldex/reporte-bancoldex-2026-07-02.pdf
   (páginas «Línea base del servicio», «Control línea base» e «Indicadores»)
   y de la lectura directa de Bancoldex/Data consolidada junio_Bancoldex 2026.xlsx
   — no inventados. Cada declaración se verificó con un arnés Node contra
   ambos archivos reales antes de escribirse aquí — ver
   docs/2026-08-05-f7-bancoldex-aranda.md.

   No se selecciona c5 (casos): su renderizador y sus criterios (dominios
   «glpi» + «alertas») están escritos para el par requerimiento/incidente de
   AF/Novaventa y para un cliente con AlertsList — ninguno de los dos aplica
   a las cuatro categorías de Aranda. El adaptador ya lee y valida el
   archivo (misma entrada que hoy recibe GLPI, ver cargarCasosOGlpi() en el
   motor); la tarjeta visual de casos queda para un siguiente change. No se
   selecciona c10 (capacidad): Bancóldex no declara esa hoja. */
window.PERFIL_BANCOLDEX = {
  id: 'bancoldex',
  nombre: 'Bancóldex',
  celula: 'Célula 3',
  extiende: 'base',

  contrato: {
    codigo: 'CN-2024112',
    inicio: '2024-11-14',
    vigenciaHasta: '2026-11-14',
  },

  lineaBase: {
    alcance: 'Administración de Bases de Datos y Servidores de Aplicación Oracle.',
    estadisticas: [
      {etiqueta: 'Alcance', valor: 'Admin. BD y Oracle', meta: 'Producción y Desarrollo/Pruebas'},
      {etiqueta: 'Activos gestionados', valor: '257', meta: 'Línea base junio 2026 (contrato: 237)'},
      {etiqueta: 'Motores', valor: 'Oracle · SQL Server · MySQL', meta: 'Más aplicaciones (Weblogic, Apex)'},
      {etiqueta: 'Vigencia', valor: '14 nov 2026', meta: 'Contrato vigente', destacada: true},
    ],
  },

  // Las cuatro metas del PDF de referencia («Indicadores», página 4):
  // Disponibilidad 99,98 %, Cumplimiento tiempos de Atención 97 %,
  // Cumplimiento entregables 99 %, Ejecución de Backups 95 %. Los nombres de
  // clave (disponibilidad/gestionServicio/entregables/backups) son los que
  // ya usa el motor — no se inventan claves nuevas.
  metas: {disponibilidad: 0.9998, gestionServicio: 0.97, entregables: 0.99, backups: 0.95},

  tarjetas: {
    seleccionadas: ['c3', 'c4', 'c6', 'c7', 'c8', 'c8m', 'c9', 'c11', 'c12'],
    presentacion: {
      c3: {items: [['Línea base'], ['Activos gestionados', '257'], ['Motores', 'Oracle · SQL Server'], ['Vigencia', 'Hasta 14/11/2026']], chip: ['ok', 'Vigente']},
      c4: {items: [['Indicadores del servicio'], ['Disponibilidad', '—', 'Meta 99,98%'], ['Gestión del Servicio', '—', 'Meta 97%'], ['Entregables', '—', 'Meta 99%']]},
      c6: {meta: 'Meta 99,98% · requiere el consolidado'},
      c7: {meta: 'Ejecución de backups por BD · Meta 95%'},
      c11: {meta: 'Meta 99,98% por motor · requiere el consolidado'},
      c12: {valor: '1 archivo', meta: 'Informe mensual Bancóldex'},
    },
  },

  fuentes: {
    // Adaptador de Aranda, carga manual (no hay GLPI). La misma entrada de
    // archivo que usa AF/Novaventa para GLPI se reutiliza — ver
    // cargarCasosOGlpi() en el motor.
    casos: {
      lector: 'tabular-xlsx',
      adaptador: 'aranda-export',
      // Alias ya normalizados (minúsculas, espacio en vez de guion bajo):
      // col()/candidatosCabecera() comparan contra norm(celda) pero NO
      // normalizan el alias, así que 'numero_del_caso' nunca matchea
      // "NUMERO_DEL_CASO" (norm() la deja en "numero del caso"). Verificado
      // contra el export real de junio-2026: 72 filas, encabezado en la
      // fila 0, sin ambigüedad.
      cabecera: {estrategia: 'primera-fila-con', campos: [['numero del caso'], ['fecha registro']]},
      columnas: {
        id: ['numero del caso'],
        tipoCaso: ['tipo de caso'],
        jerarquia: ['jerarquia'],
        // Typo real de la fuente ("INDICARDOR"); no se corrige — corregirlo
        // rompería la lectura del archivo real.
        cumplimiento: ['indicardor de cumplimiento'],
        fecha: ['fecha registro'],
        motor: ['motor'],
      },
      filtroCliente: {estrategia: 'archivo-alcance-unico'},
      jerarquia: {separador: '.'},
      sla: {estrategia: 'columna-cumplimiento', verdaderos: ['cumple'], falsos: ['no cumple']},
    },
    consolidado: {
      // Verificado contra el archivo real: la fila con «INDICADOR»/«META»
      // (una sola, sin ambigüedad) también contiene las fechas — la
      // estrategia primera-fila-con ya la resuelve sin cambios en el motor.
      // Las columnas BANCOLDEX/SETI están intercaladas por mes; solo la
      // columna BANCOLDEX trae fecha en esa fila (SETI queda vacía), así
      // que columnasPeriodo() ya selecciona la serie correcta sin ajuste.
      indicadores: {
        hojas: ['Indicador'],
        metricas: [
          {id: 'disponibilidad', aliases: ['disponibilidad'], rotulo: 'Disponibilidad de la plataforma administrada'},
          {id: 'gestionServicio', aliases: ['cumplimiento tiempos de atencion'], rotulo: 'Gestión del Servicio'},
          {id: 'entregables', aliases: ['cumplimiento entregables'], rotulo: 'Cumplimiento de entregables'},
        ],
      },
      // «Ejecucion Backups» identifica cada fila por «BD», no por
      // «Instancias» — mismo lector genérico de cargarBackups(), con el
      // nombre de hoja/columna declarado en vez del literal de AF.
      backups: {hoja: 'Ejecucion Backups', columna: 'bd'},
      // La hoja «Disponibilidad Real» trae una tabla por motor con ese
      // mismo rótulo. Verificado contra el archivo real de junio-2026: la
      // tabla existe pero sus columnas de fecha llegan solo hasta jun-25 —
      // el motor bloqueará el consolidado con un mensaje explícito hasta
      // que Bancóldex actualice esa hoja con el corte vigente. No es un
      // error del adaptador — ver docs/2026-08-05-f7-bancoldex-aranda.md,
      // "Hallazgo real: Disponibilidad Real sin corte vigente".
      disponibilidad: {estrategia: 'tabla-con-fechas', hoja: 'Disponibilidad Real', tabla: 'Disponibilidad Real'},
    },
  },

  almacen: {
    prefijo: 'informeBancoldex',
  },

  textos: {
    tituloDocumento: 'Informe Gerencial · Bancóldex',
    marcaTopbar: 'Informe Bancóldex',
    clienteHero: 'BANCÓLDEX',
    confidencialidad: 'Documento confidencial preparado por SETI para Bancóldex.',
    nombreArchivo: 'Bancoldex',
  },
};
