# Delta — inventario-tarjetas (F7, ampliación del 07/08/2026)

Motivo: al validar el entregable de Bancoldex se encontró que el HTML
exportado se generaba y se veía correcto, pero no respondía a ningún clic.
Tres de los cuatro defectos son preexistentes (desde F3 y F4) y uno de ellos
rompía también el entregable de Acción Fiduciaria, que está en producción.
Nada de esto estaba especificado: la spec describía cómo se **genera** la
tarjeta, nunca que el resultado exportado tuviera que seguir siendo
interactivo.

## ADDED Requirements

### Requirement: el entregable exportado conserva la interacción

El HTML exportado SHALL permitir abrir cada tarjeta seleccionada y ver su
panel de detalle, sin depender de estado que no sobreviva al clonado del DOM
(listeners, propiedades de nodo) ni de nodos que el propio podado elimina.

#### Scenario: cada tarjeta del entregable abre su panel

- **GIVEN** un informe exportado de cualquier perfil
- **WHEN** se hace clic en el resumen de una tarjeta seleccionada
- **THEN** se abre su panel con el contenido del periodo, sin errores en
  consola

#### Scenario: un perfil que hereda abre su entregable

- **GIVEN** un perfil con `extiende` declarado, como `bancoldex` o
  `novaventa`
- **WHEN** se abre su HTML exportado, sin los archivos de `perfiles/`
- **THEN** el informe arranca con el perfil ya resuelto que viaja en el
  estado, sin intentar cargar el perfil padre

#### Scenario: los scripts de autoría no abortan el entregable

- **GIVEN** un entregable del que el podado eliminó el panel de carga
  (`#loadPanel`, y con él `#loadSummary`)
- **WHEN** se abre y la cadena `restaurarPresetTarjetas()` →
  `aplicarPresetTarjetas()` → `actualizarResumen()` alcanza esa función
- **THEN** la función devuelve sin escribir, en vez de lanzar un `TypeError`
  que aborte el script y deje el informe inerte

#### Scenario: exportar con una tarjeta abierta

- **GIVEN** una tarjeta abierta en su modal en el momento de exportar
- **WHEN** se genera el HTML
- **THEN** el entregable conserva ese panel en su tarjeta y no lleva el modal
  de la sesión de autoría
