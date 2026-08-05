/* F7a — Perfil de cliente: Bancóldex. Datos puros — sin funciones (ver
   openspec/project.md). Extiende 'base', no 'accion-fiduciaria': el delta de
   estructuras (fuente de casos, esquema de columnas, 4 indicadores en vez de
   3, disponibilidad por motor, backups por BD, línea base con ambiente)
   supera el 30% de claves hoja permitido para heredar de un perfil de
   cliente — ver docs/2026-08-04-plan-multicliente.md y el reconocimiento en
   docs/2026-08-05-reconocimiento-bancoldex.md.

   contrato y metas.disponibilidad/cumplimientoAtencion/entregables/
   ejecucionBackups vienen de Bancoldex/reporte-bancoldex-2026-07-02.pdf
   (páginas «Línea base del servicio» e «Indicadores»), no inventados.

   tarjetas.seleccionadas trae solo 'c9' — hallazgo al verificar en
   navegador: resolverTarjetasPerfil() (motor, F3) exige al menos una
   tarjeta; un arreglo vacío no es un estado soportado, hace fallar el
   arranque. De las tarjetas del inventario compartido, casi todas llevan
   texto de presentación estático heredado de Acción Fiduciaria (c3: código
   de contrato «CN-21012025»; c4: metas «99,30 %/95 %/90 %»; c12: «Informe
   mensual Oracle») — mostrarlas con la marca Bancóldex sería una cifra o
   texto ajeno visible antes de que exista un dato real, justo lo que la
   restricción inviolable #2 prohíbe evitar aunque sea solo un placeholder.
   c9 (bolsa de horas) es la única cuyo texto ya es genérico y su
   renderizador (`renderC9`) es un editor manual sin dependencia de GLPI ni
   consolidado. F7b añade la tarjeta de casos (4 categorías) y los lectores
   de consolidado; entonces esta lista crece. */
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

  metas: {
    disponibilidad: 0.9998,
    cumplimientoAtencion: 0.97,
    entregables: 0.99,
    ejecucionBackups: 0.95,
  },

  tarjetas: {
    seleccionadas: ['c9'],
  },

  // El export Aranda ya se entrega delimitado a Bancóldex; no hay columna
  // fiable para filtrar por cliente (ver design.md de este change). No se
  // declara aliasCliente porque no se usa un filtro de columna.

  // F7a: solo la fuente de casos (Aranda). Los lectores de consolidado
  // (indicadores de cabecera de dos filas, backups por BD, línea base con
  // ambiente, disponibilidad por motor) quedan para F7b.
  fuentes: {
    casos: {
      lector: 'tabular-xlsx',
      adaptador: 'aranda-export',
      // Los alias van ya normalizados (minúsculas, espacio en vez de guion
      // bajo): col()/candidatosCabecera() comparan contra norm(celda) pero
      // NO normalizan el alias, así que 'numero_del_caso' nunca matchea
      // "NUMERO_DEL_CASO" (norm() la deja en "numero del caso"). Verificado
      // contra el export real de junio-2026 con el arnés de este change.
      cabecera: {estrategia: 'primera-fila-con', campos: [['numero del caso'], ['fecha registro']]},
      columnas: {
        id: ['numero del caso'],
        tipoCaso: ['tipo de caso'],
        jerarquia: ['jerarquia'],
        // Typo real de la fuente ("INDICARDOR"); no se corrige — corregirlo
        // rompería la lectura del archivo real (ver design.md).
        cumplimiento: ['indicardor de cumplimiento'],
        fecha: ['fecha registro'],
        motor: ['motor'],
      },
      filtroCliente: {estrategia: 'archivo-alcance-unico'},
      jerarquia: {separador: '.'},
      sla: {estrategia: 'columna-cumplimiento', verdaderos: ['cumple'], falsos: ['no cumple']},
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
