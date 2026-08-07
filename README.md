# Informe Gerencial SETI

Informe mensual que SETI entrega a sus clientes de servicios gestionados.
Es **un solo archivo HTML que se abre con doble clic**: sin servidor, sin
instalación, sin conexión a internet. Quien lo recibe carga los insumos del
mes (Excel y CSV), el informe se arma solo en el navegador y se exporta como
un entregable autocontenido en HTML o PDF.

Hoy sirve a **Acción Fiduciaria** en producción. El repositorio está a mitad
de una migración por fases hacia plataforma multicliente (Novaventa,
Bancóldex), sin que Acción Fiduciaria cambie una sola cifra.

---

## Lo irrenunciable

Tres restricciones que **no se negocian**. Romperlas destruye el producto o
reintroduce un problema ya resuelto con evidencia real:

1. **Un HTML abierto con `file://`.** No hay bundler, ni build, ni
   transpilación, ni una sola llamada de red. Toda propuesta de «esto sería
   más limpio con Vite/React/un servidor local» se rechaza, sin excepción.
2. **Acción Fiduciaria no cambia ni una cifra.** Ninguna fase puede alterar
   un número, texto o comportamiento visible de su informe. Criterio de
   aceptación: **0 diferencias** contra `main` con
   `automatizacion/verificar_ab.py`, sobre el HTML *exportado*.
3. **Python: solo librería estándar**, más `openpyxl` donde ya se usa.

El razonamiento completo, con el motivo de cada una, está en
[`openspec/project.md`](openspec/project.md). **Esa es la fuente de verdad;
esto es solo el resumen.**

---

## Por dónde empezar, según a qué vengas

| Vengo a… | Lee, en este orden |
|---|---|
| **Entender el producto** | Este archivo → [`docs/requisitos-producto.md`](docs/requisitos-producto.md) |
| **Escribir código (persona o IA)** | [`CLAUDE.md`](CLAUDE.md) → [`openspec/project.md`](openspec/project.md) → [`openspec/AGENTS.md`](openspec/AGENTS.md) |
| **Tocar el HTML o una tarjeta** | [`DESIGN.md`](DESIGN.md) → [`openspec/specs/store-reporte/spec.md`](openspec/specs/store-reporte/spec.md) |
| **Entender por qué está así** | [`docs/PATRONES.md`](docs/PATRONES.md) → [`docs/arquitectura-multicliente.md`](docs/arquitectura-multicliente.md) |
| **Saber qué pasó y cuándo** | [`docs/README.md`](docs/README.md) — índice del histórico |
| **Correr la automatización de insumos** | [`automatizacion/README.md`](automatizacion/README.md) |

---

## Mapa del repositorio

```text
informe-accion-fiduciaria 1.html   El motor. ~6.700 líneas: 28 slides, el store
                                   REPORTE, los adaptadores y las autopruebas.
perfiles/<cliente>.js              Datos del cliente. Objeto serializable, SIN
                                   funciones. Hoy: accion-fiduciaria.js
automatizacion/                    Extracción de insumos (GLPI, AlertOps,
                                   disponibilidad) + arnés A/B + pruebas.
openspec/project.md                Restricciones inviolables. Se lee primero.
openspec/AGENTS.md                 El proceso: cómo se propone, especifica,
                                   implementa y verifica un cambio.
openspec/specs/<capacidad>/        Comportamiento vigente y desplegado.
openspec/changes/<fecha>-<id>/     Propuestas en curso. Archivadas en archivo/.
docs/<fecha>-<tema>.md             Histórico narrado, sesión por sesión.
dorados/<cliente>-<AAAA-MM>.json   Huellas SHA-256 de exports de referencia.
```

Lo que **no** está versionado, a propósito: insumos reales de cualquier
cliente (`Insumos*/`, `Accion Fiduciaria/`, `Bancoldex/`, `Novaventa/`),
credenciales (`automatizacion/.env`) y el `insumos-af.js` generado. Traen
datos de casos reales y no deben salir del equipo donde se preparan.

---

## Cómo se trabaja aquí

El repositorio usa **OpenSpec**: la especificación es la puerta de revisión,
no el diff.

```text
1. Lee openspec/project.md y revisa qué changes están abiertos.
2. Abre openspec/changes/<fecha>-<id>/ con proposal, design y tasks.
3. tasks.md declara la LISTA CERRADA de archivos que vas a tocar.
   Dos changes abiertos no pueden declarar el mismo archivo.
4. Si tocas comportamiento ya especificado, escribe el delta en
   changes/<tu-change>/specs/ ANTES de tocar código.
5. Implementa. Verifica. Documenta en docs/<fecha>-<tema>.md.
6. PR contra main, revisada por alguien distinto de quien la escribió.
```

Un PR que cambia comportamiento descrito en `openspec/specs/` sin su delta
correspondiente **se rechaza sin leer el código**. Con un archivo de 6.700
líneas concentrando la mitad de los commits, esta es la regla que evita que
dos agentes en paralelo produzcan un conflicto irresoluble.

Detalle completo en [`openspec/AGENTS.md`](openspec/AGENTS.md). Para
arrancar un change con la estructura correcta: `/nuevo-change`.

---

## Verificación

```bash
# Suite completa de Python (40 pruebas)
python3 -m unittest discover -s automatizacion -p 'test_*.py' -v

# El arnés A/B se verifica a sí mismo
python3 automatizacion/verificar_ab.py --autoprueba

# Comparar dos exports reales: el criterio de la restricción #2
python3 automatizacion/verificar_ab.py export-main.html export-rama.html
```

En el navegador, con el informe abierto y los insumos del mes cargados:

```js
await REPORTE.autopruebas()          // sin archivos: invariantes del store
await REPORTE.autopruebas(archivos)  // con archivos: reglas de negocio reales
```

Una prueba que no se ejecutó se documenta como **pendiente**, nunca como
implícitamente aprobada.

---

## Estado de la migración multicliente

El estado por fase, qué está bloqueado y el siguiente paso viven en
[`TASKS.md`](TASKS.md) — es lo único que cambia cada sesión, por eso está
separado de este README. El histórico de fases ya cerradas está en
[`CHANGELOG.md`](CHANGELOG.md).

Arquitectura objetivo, con criterio de aceptación por fase:
[`docs/arquitectura-multicliente.md`](docs/arquitectura-multicliente.md).

### Deuda conocida

Registrada para que nadie la descubra tarde:

- **2 de 7 capacidades tienen spec.** Existen `perfil-cliente` y
  `store-reporte`. Faltan `exportacion`, `inventario-tarjetas`,
  `adaptadores-fuente`, `automatizacion-insumos` y, la más sensible,
  `reglas-de-negocio` — la atribución SETI, la bolsa de horas y el redondeo
  de disponibilidad solo están narrados en `docs/`, sin un `SHALL`
  verificable, y son justo donde ya hubo errores corregidos en vivo.
- **El perfil declara datos que el motor ignora.** `metas`, `celula`,
  `contrato.codigo` y `contrato.vigenciaHasta` existen en
  `perfiles/accion-fiduciaria.js` pero el motor no los consume: la meta
  99,30 % sigue escrita a mano en unos ocho puntos del HTML. Cambiar el
  perfil no produce efecto **ni error**, que es peor.
- **Nombres de cliente en el motor.** `esAccionFiduciaria()` y
  `esClienteAccion()` ya leen del perfil, pero conservan el nombre de un
  cliente en el identificador de una función que debe ser genérica.
