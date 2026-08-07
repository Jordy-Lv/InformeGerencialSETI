# F5 — Adaptadores de fuente y modelo canónico

## Resultado técnico

GLPI y AlertsList ya no calculan sus métricas directamente desde las filas
leídas. Ambos cargadores conservan nombre, firma, mensajes y publicación en
`REPORTE`, pero primero producen `CasoCanonico` y después derivan las cifras
que consumen las tarjetas existentes.

El modelo conserva `slaCumplido` y `atribuibleSeti` como valores tri-valuados.
Solo `slaCumplido === true` suma a los cumplidos; `null` permanece como dato
desconocido. La autoprueba embebida cubre ese caso y cubre dos cabeceras
candidatas, que ahora causan una fuente inválida con los índices en el mensaje.

## Configuración y alcance

`perfiles/accion-fiduciaria.js` declara columnas, estrategia de cabecera,
clasificador, SLA y la precedencia de AlertOps sobre el consolidado histórico.
La reconciliación existente entre AlertsList y consolidado continúa en
`REPORTE.reconciliaciones`, fuera del informe de cliente.

No se modificaron tarjetas, preset ni reglas visuales.

## Verificación ejecutada

- `python3 -m unittest discover -s automatizacion -p 'test_*.py' -v` →
  55 pruebas correctas.
- `node --check perfiles/accion-fiduciaria.js` y comprobación bloque a bloque
  del HTML → 10 bloques internos válidos.
- `python3 automatizacion/verificar_ab.py` entre `export-main-f3.html` y el
  export real `export-f5.html` → **0 diferencias**.
