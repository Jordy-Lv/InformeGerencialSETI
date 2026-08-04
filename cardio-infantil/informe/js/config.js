const CONFIG = {
  clienteNombre: 'Fundación Cardioinfantil',
  // Fechas de contrato sin confirmar todavía — placeholder explícito, no un
  // dato inventado que se pueda confundir con uno real.
  contrato: { codigo: 'PENDIENTE', inicio: null, fin: null },
  // Confirmado en el PPT mensual de junio 2026 (diapositiva de anexos):
  // los tres sistemas SQL Server sobre los que se reporta cada mes.
  sistemas: ['CLDBSPROD01', 'SCCM', 'SQLLAB3'],
  // Sin confirmar para Cardio Infantil — se copia el valor de Acción
  // Fiduciaria como punto de partida, no como dato verificado.
  metaDisponibilidad: 99.5,

  // El consolidado real de Cardio Infantil (export de GLPI) no es una tabla
  // plana: son 3 hojas con columnas distintas entre sí. Cada entrada dice
  // qué columnas debe tener esa hoja para considerarse válida. Una hoja
  // vacía (0 filas) es válida — significa "sin casos de ese tipo este mes",
  // no un archivo incompleto.
  hojasRequeridas: {
    'Reque_SO': ['Título', 'Cliente', 'Fecha de apertura', 'Categoría', 'Tipo'],
    'Alerta_SO': ['Título', 'Cliente', 'Fecha de apertura', 'Categoría'],
    'Requerimientos BD': ['Título', 'Cliente', 'Fecha de apertura', 'Categoría', 'Asignado a - Técnico'],
  },
};

const MESES = ['enero','febrero','marzo','abril','mayo','junio','julio',
               'agosto','septiembre','octubre','noviembre','diciembre'];
