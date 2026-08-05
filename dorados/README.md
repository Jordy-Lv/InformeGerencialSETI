# Dorados de exportación

Aquí viven las referencias verificables por cliente y periodo:

```text
dorados/<cliente>-<AAAA-MM>.json
```

Un dorado no contiene el HTML, `window.__ESTADO__` ni textos visibles en
claro. Solo conserva metadatos de identidad, conteos y huellas SHA-256 por
componente. Por eso puede versionarse sin publicar cifras, casos ni textos
reales del cliente.

## Crear una referencia

El origen debe ser el HTML completo generado por `exportarHTML()`, no la
plantilla editable:

```bash
python3 automatizacion/verificar_ab.py \
  --crear-dorado /ruta/privada/Informe-Accion-Fiduciaria-Junio-2026.html \
  --cliente accion-fiduciaria \
  --periodo 2026-06
```

Por defecto se crea `dorados/accion-fiduciaria-2026-06.json`. Si ya existe,
el comando se detiene. Para actualizar intencionalmente una referencia
revisada se agrega `--reemplazar-dorado`.

## Verificar un export

```bash
python3 automatizacion/verificar_ab.py \
  /ruta/privada/Informe-Accion-Fiduciaria-Junio-2026.html \
  --contra-dorado dorados/accion-fiduciaria-2026-06.json
```

El código de salida es `0` si todos los componentes coinciden, `1` si hay
diferencias y `2` si el export o el dorado son inválidos.

Cuando haya una diferencia, el reporte identifica el componente afectado.
Para ver los valores concretos sin sacarlos del equipo, se comparan
localmente el export de referencia y el export candidato con el modo A/B de
dos HTML.

## Pendiente de F0

Todavía falta generar la primera referencia de Acción Fiduciaria desde un
export real y completo de junio de 2026. Los insumos y el HTML de origen son
privados y nunca se agregan al repositorio; únicamente se versionará el JSON
de huellas resultante.
