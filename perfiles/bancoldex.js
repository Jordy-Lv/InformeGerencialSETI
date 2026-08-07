/* F7 — Perfil de cliente: Bancoldex. Datos puros — sin funciones (ver
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
   docs/2026-08-05-f7-bancoldex-aranda.md (rama codex/bancoldex-completo,
   probado end-to-end en navegador con los tres insumos reales de junio-2026).

   El preset solo selecciona secciones respaldadas por los insumos originales
   de junio de 2026. La disponibilidad contractual se presenta en Indicadores
   (c4); c6/c11 no se seleccionan porque «Disponibilidad Real» termina en
   jun-25. Tampoco se selecciona c9: el TYA entregado corresponde a sep-25 y
   no acredita bolsa contratada/saldo para jun-26. No se selecciona c10
   (capacidad): Bancoldex no declara esa hoja.

   c5 (casos) se selecciona desde el 06/08/2026: el renderizador de Aranda
   (dona por motor, barras por categoría) y el clasificador de tipo se
   portaron desde codex/bancoldex-completo — ver
   openspec/changes/2026-08-05-f7-bancoldex-aranda/ y
   docs/2026-08-06-aranda-alertslist-bancoldex.md. `fuentes.alertas` se
   declara con el mismo formato genérico de AF/Novaventa: AlertsList se
   interpreta (se valida y cuenta) pero no repinta el slide de casos, que
   pertenece a Aranda — ver la nota "Interacción AlertsList × Aranda" en el
   design.md de ese change. */
window.PERFIL_BANCOLDEX = {
  id: 'bancoldex',
  nombre: 'Bancoldex',
  celula: 'Célula 3',
  extiende: 'base',

  contrato: {
    codigo: 'CN-2024112',
    inicio: '2024-11-14',
    vigenciaHasta: '2026-11-14',
  },

  lineaBase: {
    alcance: 'Administración de Bases de Datos y Servidores de Aplicación Oracle.',
    exportacion: {
      servicios: '13 CI',
      activos: '257 activos',
    },
    estadisticas: [
      {etiqueta: 'Alcance', valor: 'Admin. BD y Oracle', meta: 'Producción y Desarrollo/Pruebas'},
      {etiqueta: 'Activos gestionados', valor: '257', meta: 'Línea base junio 2026 (contrato: 237)'},
      {etiqueta: 'Motores', valor: 'Oracle · SQL Server · MySQL', meta: 'Más aplicaciones (Weblogic, Apex)'},
      {etiqueta: 'Vigencia', valor: '14 nov 2026', meta: 'Contrato vigente', destacada: true},
    ],

    // Control de línea base (c3b). Cifras del entregable aprobado,
    // Bancoldex/reporte-bancoldex-2026-07-02.pdf, páginas «Línea base del
    // servicio» y «Control línea base».
    //
    // NO salen del consolidado a propósito: su hoja «Linea Base» trae otra
    // estructura (CI · MOTOR · AMBIENTE · CANTIDAD base/actual, 13 filas) y
    // suma 220/161, no los 237/257 del PDF. No existe todavía en el
    // repositorio la fuente que produce las cifras del entregable, así que
    // se declaran hasta saber de dónde salen — decisión del usuario,
    // 07/08/2026. Ver openspec/changes/2026-08-07-tarjetas-bancoldex/.
    //
    // `diferencia` no se declara en ninguna fila: la calcula el motor a
    // partir de base y actual, para que no pueda contradecir a sus operandos.
    control: {
      fuente: 'Informe gerencial Bancoldex · junio 2026',
      referenciaBase: 'Contrato 2024112 · noviembre 2024',
      referenciaActual: 'Línea base junio 2026',
      ambientes: [
        {
          nombre: 'Producción',
          filas: [
            {etiqueta: 'Bases de datos Oracle (Producción RAC)', grupo: 'Oracle', base: 14, actual: 17},
            {etiqueta: 'Bases de datos Oracle (Producción 9.16 Stand Alone)', grupo: 'Oracle', base: 10, actual: 9},
            {etiqueta: 'Bases de datos Oracle (Producción 19S Stand Alone)', grupo: 'Oracle', base: 4, actual: 1},
            {etiqueta: 'Bases de datos SQL Server (Producción Clúster)', grupo: 'SQL Server', base: 26, actual: 24},
            {etiqueta: 'Bases de datos SQL Server (Producción Stand Alone)', grupo: 'SQL Server', base: 51, actual: 53},
            {etiqueta: 'Bases de datos MySQL (Producción)', grupo: 'MySQL', base: 1, actual: 3},
            {etiqueta: 'Weblogic (Producción)', grupo: 'Aplicaciones', base: 2, actual: 3},
            {etiqueta: 'Apex (Producción)', grupo: 'Aplicaciones', base: 1, actual: 1},
          ],
        },
        {
          nombre: 'Ambientes de desarrollo y prueba',
          filas: [
            {etiqueta: 'Bases de datos Oracle (Certificación AIX 10.13)', grupo: 'Oracle', base: 19, actual: 32},
            {etiqueta: 'Bases de datos Oracle (Desarrollo y Pruebas AWS)', grupo: 'Oracle', base: 8, actual: 14},
            {etiqueta: 'Bases de datos SQL Server (Desarrollo y Pruebas AWS)', grupo: 'SQL Server', base: 97, actual: 93},
            {etiqueta: 'Bases de datos MySQL (Pruebas)', grupo: 'MySQL', base: 1, actual: 3},
            {etiqueta: 'Weblogic (Pruebas)', grupo: 'Aplicaciones', base: 1, actual: 1},
            {etiqueta: 'Weblogic (Desarrollo)', grupo: 'Aplicaciones', base: 1, actual: 1},
            {etiqueta: 'Apex (Pruebas)', grupo: 'Aplicaciones', base: 1, actual: 2},
          ],
        },
      ],
    },
  },

  // Firmantes del informe (c14). Valor inicial editable desde la interfaz:
  // una rotación de personal no debe exigir tocar código. El trazo de la
  // firma NO vive aquí — es estado del cliente en localStorage, porque un
  // perfil es un objeto serializable que se revisa en el diff.
  firmantes: [
    {clave: 'gerente', nombre: 'Santiago Amaya Cely', cargo: 'Gerente de Proyecto SETI'},
    {clave: 'lider', nombre: 'Jeyson Alzate Guzman', cargo: 'Líder técnico SETI'},
    {clave: 'supervisor', nombre: 'Leonardo Romero Morales', cargo: 'Supervisor del Contrato 2024112'},
  ],

  // Las cuatro metas del PDF de referencia («Indicadores», página 4):
  // Disponibilidad 99,98 %, Cumplimiento tiempos de Atención 97 %,
  // Cumplimiento entregables 99 %, Ejecución de Backups 95 %. Los nombres de
  // clave (disponibilidad/gestionServicio/entregables/backups) son los que
  // ya usa el motor — no se inventan claves nuevas.
  metas: {disponibilidad: 0.9998, gestionServicio: 0.97, entregables: 0.99, backups: 0.95},

  // Bancoldex no tiene todavía una fuente que acredite qué incidentes son
  // atribuibles a SETI: Aranda no trae el equivalente del log de
  // indisponibilidades de GLPI (donde un «SI» explícito lo confirma). Hasta
  // que exista, el panel muestra 0 — decisión del usuario, 07/08/2026. La
  // alternativa que estuvo activa (contar la categoría «Incidente» excluyendo
  // monitoreo) es una aproximación, y un informe en producción no puede
  // afirmar una atribución que nadie confirmó. Ver el delta de
  // openspec/changes/2026-08-05-f7-bancoldex-aranda/specs/perfil-cliente/.
  reglas: {atribucionSeti: 'sin-fuente'},

  tarjetas: {
    // c3b (control de línea base) y c14 (firmas aprobadoras) se agregan el
    // 07/08/2026: son las páginas 3 y 11 del entregable aprobado, que el
    // preset anterior no cubría.
    seleccionadas: ['c3', 'c3b', 'c4', 'c5', 'c7', 'c8', 'c8m', 'c14'],
    configuracion: {
      // c5 comparte tarjeta/modal/gráfica con AF, pero su única fuente de
      // cifras es Aranda (fuente física 'glpi': misma entrada de archivo que
      // cargarCasosOGlpi() reutiliza) y sus criterios describen lo que
      // Aranda resuelve, no GLPI+AlertsList. 'alertas' se conserva en
      // dominios y fuentes (aunque no alimenta la cifra de c5) por dos
      // acoplamientos genéricos del motor a esos dos nombres exactos:
      // actualizarVisibilidad() exige CARGA.glpi && CARGA.alertas para
      // mostrar la diapositiva s5 (REPORTE.publicar('alertas',...) lanzaría
      // "Dominio desconocido" sin el dominio registrado), y
      // EXTENSIONES_INSUMO solo admite un formato de archivo para una
      // fuente que algún tarjeta.fuentes declare (sin 'alertas' aquí,
      // validarArchivo('alertas',...) rechazaba cualquier extensión).
      c5: {
        dominios: ['casos', 'alertas'],
        fuentes: ['glpi', 'alertas'],
        criterios: [{texto: 'Aranda: casos, motores y SLA del periodo', regla: 'resuelto', dominio: 'casos'}],
      },
      // Que el mismo libro mensual traiga Logros y Mitigación en hojas
      // separadas NO se declara aquí: eso ya lo expresa
      // `fuentes.cualitativos.alcance: 'archivo-alcance-unico'`, que es lo
      // que leen cargarLogrosArchivo() y cargarMitigacionesArchivo().
      //
      // Aquí llegó a estar `c8m: {fuentes: ['logros']}` y lo único que hacía
      // era romper: `tarjeta.fuentes` alimenta EXCLUSIVAMENTE el mapa de
      // extensiones admitidas por insumo, así que reapuntarla a 'logros'
      // dejaba a 'mitigaciones' sin ninguna extensión válida y la entrada
      // «Mitigaciones y acciones (archivo alterno)» rechazaba el propio
      // libro del cliente con «Formato no permitido: …. Usa .». Retirado el
      // 07/08/2026 — c8m se queda con la fuente del inventario.
    },
    presentacion: {
      // `valores-largos`: «Oracle · SQL Server» no cabe en la columna que la
      // clase compartida dimensiona para los valores cortos de Acción
      // Fiduciaria, y se montaba sobre Vigencia. El modificador ajusta solo
      // esta tarjeta; AF, que está en producción, no se toca.
      c3: {modificadores: ['valores-largos'], items: [['Línea base'], ['Contrato', 'CN-2024112'], ['Activos gestionados', '257'], ['Motores', 'Oracle · SQL Server'], ['Vigencia', 'Hasta 14/11/2026']], chip: ['ok', 'Vigente']},
      c4: {items: [['Indicadores del servicio'], ['Disponibilidad', '—', 'Meta 99,98%'], ['Gestión del Servicio', '—', 'Meta 97%'], ['Entregables', '—', 'Meta 99%']]},
      c5: {valor: 'Pendiente de cargar', meta: 'Requiere el export de Aranda del periodo'},
      c7: {meta: 'Ejecución de backups por BD · Meta 95%'},
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
    // Mismo formato genérico que AF/Novaventa: Alert ID, Created Date y
    // Escalation Policy/Responders. Sin `data` (Bancoldex no tiene un
    // respaldo tipo Data_<mes> para alertas) y sin filtro de cliente propio:
    // esAccionFiduciaria() en cargarAlertas() ya compara contra PERFIL.nombre
    // (pese al nombre de la función — ver TASKS.md, "Higiene pendiente").
    alertas: {
      cabecera: {estrategia: 'primera-fila-con', campos: [['alert id', 'alertid'], ['created date', 'fecha'], ['escalation policy', 'escalation', 'response play']]},
    },
    cualitativos: {
      entrada: 'logros',
      alcance: 'archivo-alcance-unico',
      hojas: {logros: 'Logros', mitigaciones: 'Mitigación'},
      // Columnas adicionales del cuadro de mitigaciones (c8m). Cada valor es
      // el RÓTULO con el que se pinta en el informe, no el encabezado del
      // archivo: la columna de avance se localiza por alias («estado»,
      // «avance», …), así que el informe puede decir «Avance» aunque la hoja
      // del cliente titule esa columna «ESTADO».
      //
      // Van declaradas por perfil y no en el motor porque Acción Fiduciaria
      // entrega este contenido en otro formato — una sola hoja con «Cliente
      // · Descripción · Dato / evidencia», sin responsable, fecha ni
      // estado. Pintarlas siempre dejaría cuatro columnas vacías en un
      // informe que está en producción.
      //
      // La hoja trae el avance como fracción (0.2 = 20 %), igual que
      // PERFIL.metas.
      columnas: {
        mitigaciones: {
          responsable: 'Responsable',
          entrega: 'Fecha de entrega',
          observaciones: 'Observaciones',
          avance: 'Avance',
        },
      },
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
      // que Bancoldex actualice esa hoja con el corte vigente. No es un
      // error del adaptador — ver docs/2026-08-05-f7-bancoldex-aranda.md,
      // "Hallazgo real: Disponibilidad Real sin corte vigente".
      disponibilidad: {estrategia: 'tabla-con-fechas', hoja: 'Disponibilidad Real', tabla: 'Disponibilidad Real'},
    },
  },

  almacen: {
    prefijo: 'informeBancoldex',
  },

  textos: {
    tituloDocumento: 'Informe Gerencial · Bancoldex',
    marcaTopbar: 'Informe Bancoldex',
    clienteHero: 'BANCOLDEX',
    confidencialidad: 'Documento confidencial preparado por SETI para Bancoldex.',
    nombreArchivo: 'Bancoldex',
    // Mismo mecanismo data-perfil-carga que ya usa Novaventa para su propio
    // insumo de consolidado/alertas — hidratarTextosPerfil() lo aplica sin
    // cambios en el motor.
    carga: {
      glpiTitulo: '2. Exportación Aranda',
      glpiAyuda: 'Excel de Aranda con Número del caso, Fecha de registro, Tipo de caso, Motor e Indicador de cumplimiento.',
    },
  },
};
