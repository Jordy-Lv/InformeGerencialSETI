# Requisitos del producto

Qué debe hacer el Informe Gerencial SETI y **con qué se verifica cada cosa**.

## Cómo leer este documento

Cada requisito lleva un estado de formalización. Es la diferencia entre lo
que está blindado por una spec y lo que solo vive en el código:

| Marca | Significa |
|---|---|
| **[SPEC]** | Formalizado en `openspec/specs/` con `SHALL` + escenario verificable |
| **[CÓDIGO]** | Implementado y probado, pero **sin spec**. Nada impide que un cambio lo rompa en silencio. Es deuda |
| **[PLAN]** | Comprometido en el plan maestro, todavía no implementado |

**Este documento no crea requisitos nuevos.** Recoge los que ya rigen. Un
requisito marcado `[CÓDIGO]` no se puede citar en una revisión como si fuera
normativo — para eso hay que escribir su spec, y cada capacidad pendiente
merece su propio change.

---

## R1 — Entrega y ejecución

### R1.1 Un archivo, sin instalación **[SPEC parcial]**

El informe SHALL abrirse con doble clic desde `file://`, sin servidor, sin
build y sin conexión a internet. Ninguna dependencia externa se carga por
red: `jsPDF` y `html2canvas` viajan embebidos en el propio HTML.

*Verificación:* abrir el archivo con el equipo desconectado y comprobar que
carga insumos, calcula y exporta.
*Fuente:* restricción inviolable #1 de `openspec/project.md`.

### R1.2 Entregable autocontenido **[SPEC]**

`exportarHTML()` SHALL producir un único HTML que funcione fuera de la
carpeta del proyecto. El perfil resuelto viaja dentro de `window.__ESTADO__`
y el documento exportado no conserva ningún `script src` hacia `perfiles/`.

*Verificación:* mover el export a otra carpeta y abrirlo.
*Spec:* `perfil-cliente` → «entregable autocontenido».

### R1.3 Exportación a PDF **[CÓDIGO]**

El informe SHALL exportarse a PDF conservando el nombre de archivo
configurado en `PERFIL.textos.nombreArchivo`, en el formato
`Informe <cliente> <Mes> <Año>.pdf`.

*Nota:* la captura depende de `html2canvas` — lo que solo existe en `:hover`
o en una animación no llega al PDF. Ver [`DESIGN.md`](../DESIGN.md) §6.

---

## R2 — Carga de insumos

### R2.1 Cuatro insumos mensuales **[CÓDIGO]**

El informe SHALL aceptar el consolidado de disponibilidad (`.xlsx`), la
sábana de casos de GLPI, el consolidado de alertas de AlertOps y el registro
de logros y mitigaciones del cliente.

### R2.2 Recarga sin recargar la página **[CÓDIGO]**

Al volver a cargar un insumo modificado, el informe SHALL recalcular todo lo
que dependa de él. Fue un fallo real, diagnosticado y corregido el 4 de
agosto de 2026.

*Fuente:* `docs/archivo/2026-08-04-validacion-recarga-de-insumos.md` y su corrección.

### R2.3 Persistencia entre sesiones **[SPEC]**

El informe SHALL conservar los insumos y el estado editado entre sesiones,
con claves de almacenamiento construidas a partir del id del perfil, y SHALL
seguir leyendo las claves históricas de Acción Fiduciaria cuando la clave
nueva no exista.

*Spec:* `perfil-cliente` → «almacenamiento compatible por perfil».

---

## R3 — Integridad de los datos reportados

Esta sección es la más sensible del producto: **cada requisito de aquí
corresponde a un error real que llegó a producción o estuvo a punto.**

### R3.1 Cifra, cero confirmado y fallo son tres cosas distintas **[SPEC]**

El store SHALL distinguir una cifra real, un cero confirmado y un fallo de
carga, y la interfaz SHALL mostrarlos de forma inconfundible.

*Por qué importa:* un cero que parece «no cargado» —o al revés— le reporta a
un cliente que no hubo incidentes cuando nadie subió el archivo.
*Spec:* `store-reporte` → «diferencia entre cifra, cero confirmado y fallo».

### R3.2 Atribución a SETI: solo un «SI» explícito cuenta **[CÓDIGO]**

Un incidente SHALL considerarse atribuible a SETI **únicamente** cuando la
columna «Atribuible a SETI» diga `SI` de forma explícita. `NO`, `EN ESTUDIO`
y las celdas vacías **no** cuentan como atribuibles.

*Por qué importa:* la regla anterior contaba «en estudio» como atribuible e
inflaba el indicador. Corregido el 29 de julio de 2026 durante las pruebas
en Windows.
*Verificación:* `REPORTE.autopruebas()`, casos `F1`.
*Deuda:* esta regla **no tiene spec**. Es el argumento más fuerte para
escribir la capacidad `reglas-de-negocio`.

### R3.3 El cumplimiento se juzga sobre el valor publicado **[CÓDIGO]**

La disponibilidad SHALL publicarse con **un decimal**, y el cumplimiento
SHALL evaluarse sobre esa cifra publicada, no sobre el valor interno.

*Por qué importa:* redondear a entero convertía 99,29 % en «99 %» frente a
una meta de 99,30 %, y aparentaba un incumplimiento mucho mayor del real.
*Fuente:* `docs/2026-07-23-analisis-por-rango-y-redondeo.md`.

### R3.4 La bolsa de horas no se hereda sin editar **[CÓDIGO]**

Al cambiar de periodo, la bolsa de horas SHALL invalidarse: no puede
arrastrar el valor del periodo anterior como si fuera dato del mes actual.

*Fuente:* `docs/2026-08-04-bolsa-de-horas-persiste-entre-periodos.md`.

### R3.5 Cambiar de periodo invalida los datos anteriores **[SPEC]**

*Spec:* `store-reporte` → «cambio de periodo invalida los datos anteriores».

### R3.6 Reconciliación de indisponibilidades **[CÓDIGO]**

Cuando exista el registro manual de indisponibilidades, el informe SHALL
cruzarlo contra los incidentes ya clasificados para validar la atribución a
SETI con dato real en vez de inferencia por categoría. El cruce es
**opcional y no bloqueante**.

*Fuente:* `automatizacion/README.md` § Indisponibilidades.

### R3.7 Histórico limitado por el inicio contractual **[SPEC]**

Todo recorrido histórico SHALL limitarse inferiormente por
`PERFIL.contrato.inicio`, expresado como fecha calendario ISO, sin leer el
DOM y sin fecha por defecto: un contrato incompleto detiene el arranque.

*Spec:* `perfil-cliente` → «inicio contractual declarado por perfil».
*Estado:* implementado en F2; **A/B en cero todavía pendiente**.

---

## R4 — Multicliente

### R4.1 Un motor, perfiles como datos **[SPEC]**

SHALL existir un solo motor. Lo que varía entre clientes vive en
`perfiles/<cliente>.js` como objeto serializable **sin funciones**, con un
`id` estable.

*Spec:* `perfil-cliente` → «perfil como datos puros».

### R4.2 Fallo explícito al resolver **[SPEC]**

Resolver un id no registrado SHALL lanzar un error que incluya el id y la
lista de perfiles registrados. Un string que no resuelve falla **al
arrancar**; una función mal escrita fallaría más tarde, ya con un número
pintado en pantalla.

*Spec:* `perfil-cliente` → «resolución explícita del perfil».

### R4.3 Textos del cliente desde el perfil **[SPEC]**

Título, marca, cliente de portada y metadatos de exportación SHALL hidratarse
desde `PERFIL.textos`.

*Deuda abierta:* las **metas** (99,30 % · 95 % · 90 %) y los datos de
contrato (`CN-21012025`, vigencia) están declarados en el perfil pero el
motor **no los consume**: siguen escritos a mano en el HTML. Cambiar el
perfil no produce efecto ni error.

### R4.4 Acción Fiduciaria no cambia ni una cifra **[SPEC]**

Ninguna fase de la migración SHALL alterar una cifra, texto o comportamiento
visible del informe de Acción Fiduciaria.

*Verificación:* `python3 automatizacion/verificar_ab.py <main> <rama>` sobre
exports reales → **0 diferencias** y código de salida 0.
*Spec:* `perfil-cliente` → «equivalencia de Acción Fiduciaria».
*Fuente:* restricción inviolable #2.

### R4.5 Clientes pendientes **[PLAN]**

Novaventa y Bancoldex, cada uno con su clasificador y su detección de
encabezado como estrategia registrada. Ver el plan maestro.

---

## R5 — Automatización de insumos

### R5.1 Punto de entrada único **[CÓDIGO]**

`actualizar_informe.py` SHALL correr las extracciones y dejar el informe
listo para abrir. Es lo que se programa mensualmente.

### R5.2 Solo librería estándar **[CÓDIGO]**

`automatizacion/` SHALL limitarse a la stdlib de Python, más `openpyxl`
donde ya se usa. Corre desatendido en un servidor: cada dependencia es
fricción y superficie de falla.

*Fuente:* restricción inviolable #3.

### R5.3 Reconocimiento antes que extracción **[CÓDIGO]**

Antes de extraer de una fuente externa, SHALL existir una sonda que confirme
contra la instancia real qué vía funciona y qué esquema devuelve.

### R5.4 Los datos del cliente no salen del equipo **[CÓDIGO]**

Insumos, exports, respuestas crudas y credenciales **nunca** se versionan.
La única excepción deliberada es `automatizacion/salida/historico_casos.json`,
que solo contiene conteos mensuales ya agregados.

*Verificación:* `git check-ignore -v <ruta>` sobre cada carpeta de insumos.

---

## R6 — Verificación

### R6.1 Autopruebas embebidas **[CÓDIGO]**

`REPORTE.autopruebas()` SHALL verificar las invariantes del store sin
archivos, y las reglas de negocio con insumos reales cuando se le pasen.

*Regla de la casa:* al añadir una prueba al bloque «con archivos», confirma
que **corre de verdad**; no basta con simular la lógica en consola.

### R6.2 Suite de Python **[CÓDIGO]**

`python3 -m unittest discover -s automatizacion -p 'test_*.py'` SHALL pasar
completa antes de abrir un PR. Hoy: 40 pruebas.

### R6.3 El arnés A/B se verifica a sí mismo **[CÓDIGO]**

`verificar_ab.py --autoprueba` SHALL distinguir igualdad, una cifra
modificada y un elemento extra. Un comparador que no detecta diferencias
daría siempre «0 diferencias» y eso parecería un éxito.

### R6.4 Dorados sin datos en claro **[CÓDIGO]**

Un dorado SHALL contener solo metadatos de identidad, conteos y huellas
SHA-256 por componente — nunca el HTML, `window.__ESTADO__` ni textos
visibles. Por eso puede versionarse sin publicar cifras del cliente.

*Pendiente:* `dorados/accion-fiduciaria-2026-06.json` todavía no existe. Es
el criterio de cierre de F0.

---

## Requisitos sin spec: la deuda, en una tabla

Cinco de las siete capacidades declaradas en `openspec/AGENTS.md` no tienen
spec. Esto es lo que queda sin blindar:

| Capacidad | Qué quedaría cubierto | Riesgo si nadie la escribe |
|---|---|---|
| `reglas-de-negocio` | R3.2, R3.3, R3.4 | **El más alto.** Son las reglas donde ya hubo errores en producción, y hoy solo las sostiene un comentario en el código |
| `exportacion` | R1.2, R1.3 | El clonado del DOM y la autocontención no tienen escenario verificable |
| `adaptadores-fuente` | R2.1, R3.6 | Cada cliente nuevo puede inventar su forma de leer un Excel |
| `inventario-tarjetas` | Composición de las 28 slides | El descriptor de tarjetas se define sin contrato |
| `automatizacion-insumos` | R5.1–R5.4 | La automatización cambia sin puerta de revisión |
