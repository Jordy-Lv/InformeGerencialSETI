/* F6 — Novaventa hereda el contrato técnico de Acción Fiduciaria. Este
   archivo contiene solamente los datos que cambian en los insumos reales;
   no duplica lectores ni vistas. */
window.PERFIL_NOVAVENTA = {
  id: 'novaventa',
  nombre: 'Novaventa',
  celula: 'Célula 3',
  extiende: 'accion-fiduciaria',
  metas: {disponibilidad: 0.99, gestionServicio: 0.90, entregables: 0.80},
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
      indicadores: {hojas: ['Indicadores'], cabecera: {estrategia: 'bloque-con-fechas', campos: [['indicador'], ['meta']]}},
      capacidad: {hojas: ['Capacidad'], cabecera: {estrategia: 'primera-fila-con', campos: [['cliente'], ['tipo ci']]}},
    },
  },
  textos: {
    tituloDocumento: 'Informe Gerencial · Novaventa', marcaTopbar: 'Informe Novaventa',
    clienteHero: 'NOVAVENTA', confidencialidad: 'Documento confidencial preparado por SETI para Novaventa.',
    nombreArchivo: 'Novaventa',
  },
  almacen: {prefijo: 'informeNovaventa'},
};
