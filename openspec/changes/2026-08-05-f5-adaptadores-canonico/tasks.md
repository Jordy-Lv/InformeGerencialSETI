# F5 — Adaptadores de fuente y modelo canónico

F4 quedó cerrado en `fe2ed14`; no hay otro change activo que reserve los
archivos productivos de esta fase.

## Implementación

- [x] Declarar fuentes de casos y alertas de Acción Fiduciaria como datos.
- [x] Implementar validación de `CasoCanonico`, adaptadores y resolución de
  cabecera no ambigua.
- [x] Migrar GLPI y AlertsList sin cambiar su firma ni sus salidas públicas.
- [x] Asegurar que SLA desconocido no se contabiliza como cumplimiento.
- [x] Añadir especificación y pruebas de conformidad.
- [x] Ejecutar la suite y comprobaciones de sintaxis.
- [ ] Ejecutar A/B real con el preset predeterminado.
- [ ] Registrar la evidencia de cierre.
