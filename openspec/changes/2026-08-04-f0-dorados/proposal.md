# F0 — Dorados persistentes para la verificación de exportaciones

## Contexto

`automatizacion/verificar_ab.py` ya compara dos HTML exportados y demuestra
con `--autoprueba` que detecta regresiones. F0 conserva un gap: no existe el
mecanismo persistente `dorados/<cliente>-<AAAA-MM>.json` definido por el plan
maestro, por lo que cada comparación todavía depende de conservar dos HTML
completos fuera del repositorio.

Los HTML exportados y sus valores visibles son datos reales de cliente y no
se pueden versionar. El dorado debe permitir una comparación exacta sin
copiar esos valores al repositorio.

## Propuesta

Extender el arnés para crear y verificar dorados deterministas por cliente y
periodo. Cada dorado guardará únicamente huellas SHA-256 y conteos de los
componentes que el arnés ya extrae; no guardará el estado ni los textos
visibles en claro.

La comparación HTML contra HTML existente se conserva sin cambios.

## Fuera de alcance

- Producir el export real completo de junio de 2026: los insumos reales no
  están disponibles en este checkout.
- Cambiar `informe-accion-fiduciaria 1.html`.
- Agregar perfiles de cliente o cerrar F1.
- Introducir dependencias nuevas.
