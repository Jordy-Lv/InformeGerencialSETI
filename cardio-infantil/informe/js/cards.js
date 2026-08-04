// Cada tarjeta viene del inventario en
// docs/2026-08-03-inventario-tarjetas-cardio-infantil.md. Las marcadas como
// "pendiente" ahí no tienen fuente de datos confirmada todavía (Zabbix,
// contrato, herramienta de backups) — se declaran igual, en estado
// "sin-dato" fijo, para que el panel exista y el vacío se vea a propósito
// ("Pendiente de cargar"), no como una casilla olvidada. Sin `grafico`: al
// no ser clicables (ver render.js), nunca se invoca.
const DEFINICION_TARJETAS = [
  {
    id: 'casos',
    titulo: 'Total de casos',
    unidad: '',
    valor: s => s.indicadores.casos.alertas + s.indicadores.casos.requerimientos,
    estado: () => 'neutral',
    narrativa: s => {
      const c = s.indicadores.casos;
      return `Se registraron ${c.alertas} alertas y ${c.requerimientos} requerimientos de sistema operativo en el período (Casos de Base de Datos se reporta aparte).`;
    },
    grafico: s => ({
      type: 'bar',
      data: {
        labels: ['Alertas', 'Requerimientos SO'],
        datasets: [{
          data: [s.indicadores.casos.alertas, s.indicadores.casos.requerimientos],
          backgroundColor: ['#2a568f', '#B0780B']
        }]
      },
      options: { plugins: { legend: { display: false } } }
    })
  },
  {
    id: 'casosBD',
    titulo: 'Casos de Base de Datos',
    unidad: '',
    valor: s => s.indicadores.casos.casos_bd,
    estado: () => 'neutral',
    narrativa: s => `Se atendieron ${s.indicadores.casos.casos_bd} casos de base de datos en el período (requerimientos técnicos con técnico asignado y solución registrada).`,
    grafico: s => ({
      type: 'doughnut',
      data: {
        labels: ['Casos de BD'],
        datasets: [{ data: [s.indicadores.casos.casos_bd], backgroundColor: ['#6E4FA3'] }]
      },
      options: {}
    })
  },
  {
    id: 'indicadoresServicio',
    titulo: 'Indicadores del servicio',
    unidad: '%',
    valor: () => null,
    estado: () => 'sin-dato',
    narrativa: () => 'Sin fuente confirmada: disponibilidad, gestión del servicio y cumplimiento de entregables no están en el consolidado de GLPI. Pendiente de sondeo (ver inventario de tarjetas).',
  },
  {
    id: 'disponibilidad',
    titulo: 'Disponibilidad global',
    unidad: '%',
    valor: () => null,
    estado: () => 'sin-dato',
    narrativa: () => 'Sin fuente confirmada. Candidato: Zabbix (mencionado en el PPT mensual), pendiente de sondear.',
  },
  {
    id: 'backups',
    titulo: 'Gestión de backups',
    unidad: '',
    valor: () => null,
    estado: () => 'sin-dato',
    narrativa: () => 'Sin fuente confirmada: hoy es una captura de pantalla en el PPT, no datos estructurados. Pendiente identificar la consola de backups.',
  },
  {
    id: 'logros',
    titulo: 'Logros del servicio',
    unidad: '',
    valor: s => s.cualitativo.logros.length || null,
    estado: s => s.cualitativo.logros.length ? 'neutral' : 'sin-dato',
    narrativa: s => s.cualitativo.logros.length
      ? s.cualitativo.logros.join(' ')
      : 'Sin cargar todavía. El contenido cualitativo (equivalente a los bloques "Tratamiento/Beneficio" del PPT actual) se carga como texto, igual que en Acción Fiduciaria.',
  },
  {
    id: 'mitigaciones',
    titulo: 'Mitigaciones y riesgos',
    unidad: '',
    valor: s => s.cualitativo.mitigaciones.length || null,
    estado: s => s.cualitativo.mitigaciones.length ? 'neutral' : 'sin-dato',
    narrativa: s => s.cualitativo.mitigaciones.length
      ? s.cualitativo.mitigaciones.join(' ')
      : 'Sin cargar todavía.',
  },
  {
    id: 'bolsaHoras',
    titulo: 'Bolsa de horas',
    unidad: 'h',
    valor: () => null,
    estado: () => 'sin-dato',
    narrativa: () => 'Sin confirmar si el contrato de Cardio Infantil maneja bolsa de horas.',
  },
  {
    id: 'disponibilidadPorSistema',
    titulo: 'Disponibilidad por sistema',
    unidad: '',
    valor: () => null,
    estado: () => 'sin-dato',
    narrativa: () => `Sin fuente confirmada, para: ${CONFIG.sistemas.join(', ')}. Candidato: Zabbix.`,
  },
];
