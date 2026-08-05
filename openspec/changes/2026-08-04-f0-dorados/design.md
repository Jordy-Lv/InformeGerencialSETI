# Diseño — dorados A/B sin datos reales en claro

## Decisiones

### El dorado contiene huellas por componente

Se serializa canónicamente cada componente que ya compara el arnés:

- `window.__ESTADO__` completo.
- La lista ordenada de textos de cada selector visible objetivo.

El JSON guarda el SHA-256 y el número de elementos de cada componente, más
una huella total. Esto detecta cambios de valor, orden o cantidad sin
versionar cifras, nombres de casos ni textos del cliente.

Se descartó guardar el snapshot extraído en claro: sería más cómodo para
diagnosticar, pero contradiría la prohibición de commitear datos reales. Ante
una diferencia, el arnés identifica el componente; el diagnóstico detallado
se obtiene comparando localmente los dos HTML con el modo A/B existente.

### Formato determinista y versionado

El formato lleva `esquema: 1`, `cliente`, `periodo`, `huella_total` y
`componentes`. No incluye fecha de generación, ruta de origen ni otros datos
variables, de modo que crear dos veces el mismo dorado produce los mismos
bytes.

El nombre obligatorio es `<cliente>-<AAAA-MM>.json`. El cliente usa un id en
minúsculas separado por guiones y el periodo se valida como mes calendario.

### El periodo declarado se contrasta con el export

Al crear el dorado, `periodo.mes` de `window.__ESTADO__` se interpreta como
mes base cero, igual que el informe. Si no coincide con `--periodo`, el arnés
falla y no escribe nada. Esto evita etiquetar junio con un export de julio.

### Escritura segura

La creación rechaza sobrescribir un dorado existente. Reemplazar una
referencia requiere `--reemplazar-dorado`, una intención explícita que puede
revisarse en el diff.

## Compatibilidad

La invocación vigente con dos HTML y `--autoprueba` mantiene su interfaz y
sus códigos de salida. Todo se implementa con biblioteca estándar.
