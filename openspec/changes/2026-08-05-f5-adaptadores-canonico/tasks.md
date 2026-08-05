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
- [x] Ejecutar A/B real con el preset predeterminado.
- [x] Registrar la evidencia de cierre.

## Evidencia de cierre

El 5 de agosto de 2026 se comparó el export completo
`/Users/yordypardopajaro/Downloads/Otros/export-f5.html` contra
`/Users/yordypardopajaro/Downloads/Otros/export-main-f3.html`, ambos creados
con los mismos insumos reales y el preset predeterminado. La ejecución de
`python3 automatizacion/verificar_ab.py` informó `0 diferencias`.
