/* Perfil base: SETI, sin cliente concreto. Datos puros — sin funciones (ver
   openspec/project.md, "Multicliente por configuración, no por copia").
   F7 lo introduce como raíz para clientes que no comparten lo bastante con
   accion-fiduciaria como para heredar de ella (regla del 30% de claves hoja,
   docs/2026-08-04-plan-multicliente.md). No representa a ningún cliente:
   resolverPerfil('base') sin más resuelve, pero falla explícitamente al
   validar contrato.inicio (F2) porque este perfil no lo declara a propósito
   — cada perfil que extienda base debe aportar su propio contrato. */
window.PERFIL_BASE = {
  id: 'base',
  nombre: 'SETI',
  celula: null,
  extiende: null,

  contrato: {},

  metas: {},

  tarjetas: {
    seleccionadas: [],
  },

  aliasCliente: [],

  fuentes: {},

  almacen: {
    prefijo: 'informeBase',
  },

  textos: {
    tituloDocumento: 'Informe Gerencial · SETI',
    marcaTopbar: 'Informe Gerencial SETI',
    clienteHero: 'SETI',
    confidencialidad: 'Documento confidencial preparado por SETI.',
    nombreArchivo: 'Informe',
  },
};
