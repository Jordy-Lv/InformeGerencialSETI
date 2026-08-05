# Plan maestro — de un cliente a plataforma multicliente (Informe Gerencial SETI)

**Para:** quien continúe (Claude, otra IA, u otra persona del equipo).
**Qué es esto:** el plan aprobado de la refactorización multicliente completa
del proyecto. Es el documento de referencia único para todas las fases
(F0–F11) y para todas las herramientas/IAs que trabajen en paralelo sobre
este repo. **Léelo entero antes de tocar** `informe-accion-fiduciaria 1.html`,
cualquier archivo de `automatizacion/`, o de crear `openspec/` — este
documento define el vocabulario, las restricciones inviolables y el criterio
de aceptación de cada fase. Si una tarea concreta contradice algo escrito
aquí, se detiene y se pregunta antes de proceder; este plan no se reinterpreta
por conveniencia de una sesión.

**Origen:** sesión de planificación del 04/08/2026, a partir de: (a) la
revisión del PR #5 (Cardio Infantil, cerrado con feedback — ver
[docs/2026-08-03-inventario-tarjetas-cardio-infantil.md](2026-08-03-inventario-tarjetas-cardio-infantil.md)
si se recupera de `origin/cardio-infantil/inventario-tarjetas`), (b) una
exploración completa del código (`informe-accion-fiduciaria 1.html` +
`automatizacion/`) y del historial de `main`, y (c) inspección directa de los
insumos reales de Bancóldex y Novaventa que el usuario agregó al árbol de
trabajo (`Bancoldex/`, `Novaventa/`, sin versionar).

**Rama de esta fase (F0):** `refactor/multicliente-f0-fundacion`, creada
desde `main` (`aca70a0`).

---

## Contexto

Hoy el proyecto produce **un** informe gerencial mensual, para **un** cliente
(Acción Fiduciaria, Célula 3). Todo el producto vive en
`informe-accion-fiduciaria 1.html`: 6 525 líneas, ~555 KB de lógica propia,
**49 % de los 57 commits del repo tocan ese archivo**. Las 10 tarjetas están
escritas a mano, los 7 criterios de validación son una lista fija, y hay 48
literales "Acción Fiduciaria" (7 de ellos filtros de negocio reales, no
texto).

El objetivo es que deje de ser el informe de un cliente y pase a ser una
plataforma: un **inventario de tarjetas** del que cada célula elige las que
aportan a su cliente, con **presets por cliente**, validaciones propias según
cómo llega su información, y **herencia** para que un cliente parecido a otro
no cueste código nuevo.

Ya hay evidencia real de tres clientes nuevos en el árbol (`Bancoldex/`,
`Novaventa/`, y Cardio Infantil en ramas). El intento anterior de sumar un
cliente (PR #5) lo hizo **copiando** el árbol de automatización — 11 de 13
funciones duplicadas. Ese PR ya se cerró con feedback. Este plan es la
alternativa: **multicliente por configuración, no por copia**.

El plan se ejecutará con varias IAs en paralelo. Por eso la especificación
(OpenSpec) no es adorno: es el mecanismo que impide que se desvíen.

---

## Decisiones ya tomadas

| Decisión | Resuelto |
|---|---|
| **Casos de Bancóldex** | Export manual de Aranda (`Casos + tareas BD <mes>.xlsx`). Se construye adaptador de carga manual; **no** hay extractor automático en este alcance. El sondeo de una API de Aranda queda anotado como pregunta abierta, no bloquea. |
| **Alertas de Novaventa** | AlertOps **ya está activado**, y además debe poder interpretarse desde el consolidado `Data_<mes>.xlsx`. → Un dominio admite **varias fuentes alternativas con precedencia**. |
| **PR #5 / Cardio** | Cerrado con feedback. Se recupera el inventario de tarjetas (PR #1) a `docs/` y sus aportes reales entran como PRs pequeños al núcleo compartido. |
| **Nombres** | Repo → `InformeGerencialSETI`. Artefacto → `informe.html` (plantilla) y `informe-<cliente>-<periodo>.html` (salida). |

---

## Principio rector: dónde se corta la línea entre dato y código

Es la regla que decide todo lo demás, y está redactada para ser decidible sin
discusión:

> **Es dato** si al cambiarlo solo cambian números, etiquetas o rutas que un
> algoritmo existente ya sabe procesar.
> **Es código (estrategia registrada)** si al cambiarlo cambia *cómo se
> decide algo* o *cómo se recorre una estructura*.
> **Prueba práctica:** ¿podrías revisarlo con el líder de cuenta sin
> explicarle qué es una función? Sí → dato. No → estrategia.

Aplicada a la evidencia real:

- **Dato**: meta 0,993 vs 0,99 vs 0,9998 · hoja `Mitigación` vs `Hallazgos` ·
  separador de jerarquía `>` vs `.` · entidad GLPI · lista de CI y motores ·
  orden y selección de tarjetas.
- **Código**: clasificar por categoría (AF/Novaventa) vs por `TIPO_DE_CASO`
  (Bancóldex) vs por hoja de origen (Cardio) · detección de encabezado
  (primera fila vs bloque con fechas vs dos filas cruzadas) · SLA desde
  "Tiempo para resolver excedido" vs desde `INDICARDOR DE CUMPLIMIENTO`.
- **Campo opcional del modelo canónico**: `ambiente` (solo Bancóldex), tipo
  `cambio` (solo Bancóldex), `casos_bd` (Cardio).

**Corolario duro:** ningún mecanismo nuevo se acepta sin **dos clientes con
evidencia real** que lo necesiten. Si solo Bancóldex necesita `AMBIENTE`, es
un campo opcional del canónico — no una dimensión de primera clase en la UI
de todos.

---

## Arquitectura objetivo

### 1. Perfil de cliente — datos puros con herencia explícita

Un perfil es un **objeto serializable a JSON. No contiene funciones.** Cuando
necesita comportamiento, nombra una estrategia registrada por string.

Tres razones, en orden de peso:
1. Tiene que sobrevivir a `exportarHTML()` — el perfil resuelto viaja dentro
   de `window.__ESTADO__` (línea 4449). Una función no se serializa.
2. Un string que no resuelve **falla al arrancar**, con la lista de nombres
   desconocidos. Una función mal escrita falla más tarde, ya con un número
   pintado en pantalla.
3. Si el perfil pudiera llevar funciones, se convertiría en un segundo
   código sin pruebas. Con varias IAs, esa es la deriva por defecto: *"lo
   meto en el perfil, así no toco el núcleo"*. El perfil debe ser tan
   aburrido que no tiente.

```
perfiles/
  base.js                  # SETI, cualquier célula
  accion-fiduciaria.js     # extiende: 'base'
  novaventa.js             # extiende: 'accion-fiduciaria'
  bancoldex.js             # extiende: 'base'
  cardio-infantil.js       # extiende: 'base'  (bloqueado hasta sondeo)
```

Forma: `{ id, nombre, celula, extiende, contrato:{numero,inicio,fin,...},
metas:{}, ci:{sistemas,motores,ambientes?}, fuentes:{},
tarjetas:{hereda,agrega,quita,reordena,ajusta}, textos:{}, almacen:{prefijo} }`

**Semántica de la herencia** — `resolverPerfil(id)` recorre la cadena y
aplica `fusionarProfundo` (línea 4817, **se reutiliza, no se escribe otro
merge**):
- Objetos → fusión profunda. Arreglos → reemplazo total (semántica que
  `fusionarProfundo` ya tiene; cambiarla rompería `chart()`).
- Listas con identidad (`tarjetas`, `ci.sistemas`) → operadores explícitos
  `hereda/agrega/quita/reordena`. Sin esto, *"¿por qué desapareció la tarjeta
  que heredé?"* no tiene respuesta legible.
- Borrado explícito con el centinela `'@heredado:borrar'` (string, no `null`
  ni `undefined`: `undefined` desaparece al serializar y `null` es un valor
  legítimo — `slaCumplido:null` significa "la fuente no lo dice").
- **Sin herencia múltiple.** Un solo `extiende`.

**Quién hereda de quién, y la regla que lo decide:**
- **Novaventa extiende `accion-fiduciaria`.** La evidencia obliga: misma
  instancia GLPI, mismas columnas exactas, misma taxonomía de categorías,
  hojas `Disponibilidad`/`Backups`/`Logros` idénticas. Su delta completo son
  ~8 claves.
- **Bancóldex extiende `base`.** Tendría que sobrescribir casi todo: fuente
  de casos, esquema de columnas, separador, origen del SLA, 4 indicadores en
  vez de 3, `Linea Base` con `AMBIENTE`, `Ejecucion Backups` con columna
  `BD`, `Indicador` con encabezado de dos filas cruzadas `BANCOLDEX|SETI`,
  `Casos` con tipo `Cambio`, `Disponibilidad Real` por MOTOR.
- **Regla ejecutable:** un perfil solo puede extender a otro perfil de
  cliente si sobrescribe **menos del 30 % de las claves hoja** del padre.
  Por encima, extiende `base`. Autoprueba `perfil/herencia-no-es-fork`
  cuenta y falla. Un umbral arbitrario pero **verificable** vale más que un
  criterio de gusto sujeto a la IA de turno.

**Lo que el perfil arregla de paso:**
- Las 6 funciones que hoy leen la fecha de contrato del **DOM editable**
  `[data-k="finicio"]` con fallback `new Date(2025,8,1)` (líneas 1794, 2381,
  3082, 3139, 3245, 3291, 3365) pasan a leer `PERFIL.contrato.inicio`. El DOM
  se invierte: pasa a ser una vista que escribe al perfil, nunca la fuente.
  Hoy ese fallback puede recortar el histórico del cliente equivocado sin
  que nada avise.
- Claves de almacén: `IDB_NAME='informeAF'` (2507),
  `'informeAF:posiciones'` (4072), `'informeAF:bolsa:'` (5767) →
  `claveAlmacen(sufijo)` = `informe:<perfilId>:<sufijo>`. Migración de solo
  lectura: si existen las viejas y no las nuevas, se leen sin reescribirlas.
- El paquete de insumos conserva `window.__INSUMOS__` y suma un campo
  `perfil`; si no coincide con `PERFIL.id`, **se rechaza con error
  visible**. (La rama de Cardio usaba `window.__INSUMOS_CARDIO__`: evita la
  colisión, pero al precio de que cargar el paquete equivocado no haga
  nada, en silencio.)

### 2. Inventario de tarjetas — descriptor y derivación

```js
{
  id: 'casos',                        // estable, no 'c5'
  legado: {tarjeta:'tk-c5', slide:'s5', dashboard:'dashboard-c5'},
  seccion: 'servicio', orden: 30, titulo, kicker, icono,
  dominios: ['glpi','alertas'], requiere: 'todos'|'alguno', dependeDe: ['casos'],
  resumen: 'resumen-casos',           // estrategia -> {etiqueta,valor,meta,chip}
  detalle: {componente:'historico'|'radar-ci'|'tabla'|'propio', opciones:{...}},
  vacio: {valor:'Pendiente de cargar', meta:'Requiere AlertsList y GLPI del periodo'},
  criterio: {texto:'GLPI: requerimientos, incidentes y SLA', regla:'resuelto'} | null,
  validaciones: [], fuentes: ['glpi','alertas'], exportable: true
}
```

Los dos componentes ya parametrizados encajan sin tocarlos — y son la prueba
de que el contrato es viable: `montarHistorico` (línea 4932, con presets
3M/6M/12M/Todo) y `montarRadarCI` (línea 6032, ya reutilizado por dos
tarjetas con `opts.textos`). Sus firmas actuales **ya son** el
`detalle.opciones` del descriptor. `componente:'propio'` es la puerta de
escape para c3 (ficha contractual) y c9 (bolsa), y cada uso debe justificarse
en el doc de sesión.

**El pago — todo lo que hoy es lista fija pasa a derivarse del inventario:**

| Hoy | Pasa a ser |
|---|---|
| `criteriosCarga()` (1674), 7 criterios fijos | `INVENTARIO.seleccionadas(PERFIL).map(t=>t.criterio).filter(Boolean)` |
| `EXTENSIONES_INSUMO` (1652) | unión de `fuentes` de las tarjetas seleccionadas |
| `DOMINIOS` (1588), array literal de 10 | unión de `dominios` + núcleo |
| `renderAll()` (6170), `renderC3();renderC4();…` | iteración sobre las seleccionadas |
| recolección de páginas del PDF (6274) | filtro por `exportable` |

Consecuencia: **añadir una tarjeta extiende la validación sola, y quitar una
deja de bloquear el PDF por un insumo que nadie usa.** Hoy, sumar la tarjeta
"Casos de Base de Datos" de Cardio exigiría tocar cinco listas a mano;
olvidar una es un bug silencioso.

**Modal de selección** — reutiliza `dashboard-modal` (línea 6184). Reglas no
opcionales: una tarjeta con `dependeDe` insatisfecho aparece deshabilitada
**con el motivo escrito**; al deseleccionar se muestra en vivo qué criterios
de carga desaparecen (quitar una tarjeta relaja la validación del PDF, y eso
no puede pasar en silencio). Persistencia en dos niveles:
`informe:<perfil>:preset-tarjetas` en localStorage (override del consultor)
sobre `PERFIL.tarjetas` (default entregado). Al exportar viaja la selección
**resuelta** en `window.__ESTADO__.perfil`.

### 3. Adaptadores de fuente y modelo canónico

```
CasoCanonico = {
  id, fecha, cliente, origen,
  tipo: 'requerimiento'|'incidente'|'alerta'|'cambio'|'caso_bd'|'otro',
  categoria, jerarquia:[],
  slaCumplido: true|false|null,      // null = la fuente no lo dice
  motor, ambiente,                    // opcionales
  atribuibleSeti: true|false|null
}
```

Los `null` tri-valuados son el corazón del diseño, y no son teoría: el commit
`e34ad12` ("Un caso no se asume atribuible a SETI por defecto — solo un SI
explícito cuenta") y el hallazgo F1 de la auditoría del 02/08 dicen
exactamente esto. Colapsar "no sé" a `false` o `true` es cómo se inventan
números. Bancóldex lo hace inevitable: su SLA sale de `INDICARDOR DE
CUMPLIMIENTO` con valores `Cumple`/`No cumple` y celdas vacías.

**Advertencia de diseño:** no normalizar "a la forma que AF tiene hoy". AF no
tiene `ambiente` ni tipo `Cambio`; si el canónico se calca de AF, los
accidentes de AF se vuelven ley.

**Declaración de fuente** (todo lo posible como dato; lo demás, estrategia
nombrada):

```js
// AF / Novaventa — 'glpi-export'
casos: {
  lector:'tabular-xlsx',
  cabecera:{estrategia:'primera-fila-con', campos:[['entidad'],['fecha de apertura'],['categoria','tipo']]},
  columnas:{id:['id'], entidad:['entidad'], fecha:['fecha de apertura'],
            categoria:['categoria','categoría'], tipo:['tipo'],
            slaExcedido:['tiempo para resolver excedido']},
  filtroCliente:{campo:'entidad', estrategia:'contiene-normalizado', valor:'accion fiduciaria'},
  jerarquia:{separador:'>'}, clasificador:'glpi-por-categoria',
  sla:{estrategia:'columna-excedido', verdaderos:['si','sí','yes','1']}
}
// Novaventa: SOLO cambia filtroCliente.valor -> 'novaventa'

// Bancóldex — 'aranda-export'
casos: {
  cabecera:{estrategia:'primera-fila-con', campos:[['numero_del_caso'],['fecha_registro']]},
  columnas:{id:['numero_del_caso'], tipoCaso:['tipo_de_caso'], jerarquia:['jerarquia'],
            cumplimiento:['indicardor de cumplimiento'],   // typo real de la fuente
            fecha:['fecha_registro'], proyecto:['proyecto']},
  filtroCliente:{campo:'proyecto', estrategia:'contiene-normalizado', valor:'bancoldex'},
  jerarquia:{separador:'.'}, clasificador:'aranda-por-tipo-de-caso',
  sla:{estrategia:'columna-cumplimiento', verdaderos:['cumple'], falsos:['no cumple']}
}
```

El typo `INDICARDOR` y el doble espacio en `Casos  + tareas BD junio
2026.xlsx` se declaran **tal cual**, con comentario de por qué no se
"arreglan": corregirlos rompería la lectura del archivo real.

**Fuentes alternativas con precedencia** (lo que el usuario pidió para
Novaventa). El proyecto **ya tiene** esta regla de negocio para AF —
*"AlertsList manda para el mes en curso; el consolidado solo aporta meses
previos"* — hoy escrita a mano dentro de `cargarAlertas`. Se generaliza:

```js
alertas: {
  origenes: [
    {id:'alertops',          precedencia:1, ambito:'mes-en-curso', ...},
    {id:'consolidado-data',  precedencia:2, ambito:'historico',    ...}
  ],
  alDiscrepar: 'reconciliar'   // registra en REPORTE.reconciliaciones, no bloquea
}
```
Novaventa declara los dos orígenes; si AlertOps aún no trae datos del
periodo, el consolidado `Data_<mes>` lo cubre, y la diferencia se registra
como reconciliación (control interno, nunca visible al cliente). AF hereda
el mismo mecanismo sin cambiar una cifra.

**Detección de encabezado — el punto donde el sistema puede mentir.**
`filaCabecera` (línea 1882) devuelve la primera fila que contiene todos los
campos. Con la evidencia nueva eso es peligroso:
- **Novaventa `Indicadores`** tiene dos bloques: metas en f2–f5 (sin fechas)
  y el histórico real en f7–f10. `filaCabecera` matchearía el primero →
  **metas leídas como serie histórica**. Un número plausible y falso, el
  peor tipo.
- **Bancóldex `Indicador`** tiene encabezado de dos filas (f2 meses, f3
  `BANCOLDEX|SETI`). Un solo índice no puede describirlo.

Estrategias registradas: `primera-fila-con` (comportamiento actual, literal)
· `bloque-con-fechas` (Novaventa) · `cabecera-de-dos-filas` (Bancóldex) ·
`por-hoja-de-origen` (Cardio, cuando se confirme).

**Regla dura transversal:** si más de un candidato matchea y la estrategia no
sabe desempatar, **no se elige ninguno** — el dominio se publica `invalido`
con los candidatos en las notas. Vale aceptar que un cliente nuevo falle al
primer intento a cambio de que nunca invente.

**Pipeline:** `archivo → lector → matriz → cabecera(estrategia) →
mapeoColumnas → filtroCliente → filtroPeriodo → clasificador+sla →
CasoCanonico[] → REPORTE.publicar(...)`. `cargarGlpi`/`cargarAlertas`/
`cargarConsolidado` conservan nombre y firma; su cuerpo pasa a ser una
llamada al pipeline. `cargarConsolidado` (línea 3884) itera
`PERFIL.fuentes.consolidado.hojas`, así que `Capacidad` (Novaventa) y `Linea
Base` (Bancóldex) son **entradas de datos, no ramas de código**.

### 4. Patrones — siete decisiones defendidas

1. **Registry** para tarjetas y estrategias. No un contenedor DI: no hay red
   (`file://`), no hay módulos, no hay ciclo de vida; y el registro debe
   sobrevivir al clonado del DOM en `exportarHTML`. Beneficio extra: las
   claves del registro son **el vocabulario cerrado** que la spec restringe
   — una IA no puede inventar `clasificador:'lo-que-se-me-ocurrió'` sin que
   el arranque falle.
2. **Herencia por resolución de datos** (`resolverPerfil` +
   `fusionarProfundo`), no herencia de clases. `class PerfilNovaventa
   extends PerfilAF` invita a sobrescribir métodos, y sobrescribir métodos
   es el camino que produjo `insumos_cardio.py`. Descartado también
   Builder: rompería la serialización.
3. **Strategy nombrada por string** para clasificación, cabecera y SLA.
   Contra Template Method: obliga a jerarquía de clases y hace imposible
   responder desde los datos *"¿qué gancho sobrescribió cada cliente?"* —
   justo la pregunta de auditoría de este proyecto. Con Strategy, `grep
   clasificador: perfiles/` responde en una línea. Y el camino de AF queda
   **literalmente intacto**.
4. **Adapter + Modelo Canónico.** El innegociable. Sin canónico, cada
   adaptador alimenta las tarjetas directo y las tarjetas se llenan de
   ramas por cliente — el mismo problema, un nivel más arriba. Es además el
   único lugar donde "fallar ruidosamente" se puede *representar*.
5. **Extender el Observer que ya existe (`REPORTE`)** y **no** introducir
   librería de estado. Decisión de *no* aplicar un patrón: `REPORTE` ya
   tiene coalescing por microtask y 5 estados explícitos; pasar de 2 a ~15
   suscriptores sigue siendo trivial. Un store tipo Redux reescribiría la
   única parte bien hecha, contra la cual asertan las 47 autopruebas.
6. **Anti-Corruption Layer en Python**: `insumos.py` genérico parametrizado
   por perfil + `perfiles/<cliente>.py` solo con lo que difiere. Respuesta
   directa a `insumos_cardio.py`. Se **prohíbe en `project.md`** crear
   archivos `insumos_<cliente>.py`.
7. **Fuente única para las reglas compartidas JS↔Python**
   (`reglas/casos.json`). Hoy `clasificar_caso_glpi` está implementada dos
   veces y la tabla de casos duplicada a mano en `test_insumos_af.py` y en
   `REPORTE.autopruebas`. Con 4 clientes serían 8 tablas. *Honestidad:*
   esto **no unifica las dos implementaciones** — transpilar violaría la
   restricción de stdlib. Elimina la divergencia **silenciosa**, que es el
   90 % del valor por el 10 % del costo.

**Descartados con nombre:** Factory/Abstract Factory (sería un `switch` con
ceremonia) · Decorator sobre tarjetas (volvería no evidente el orden del
DOM, que es justo lo que html2canvas captura) · Command/Undo para el preset
(ritual sobre un arreglo corto) · Event Bus aparte (`REPORTE` ya es el bus;
dos canales, dos verdades) · Web Components (Shadow DOM rompería html2canvas
y el clonado de `exportarHTML`).

---

## OpenSpec — estructura y cómo impide la deriva

```
openspec/
  project.md      # las 3 restricciones inviolables, en la primera pantalla
  AGENTS.md       # cómo trabaja una IA aquí
  specs/          # la verdad ACTUAL, desplegada
    perfil-cliente/ inventario-tarjetas/ adaptadores-fuente/
    store-reporte/ exportacion/ automatizacion-insumos/ reglas-de-negocio/
  changes/<fecha>-<id>/
    proposal.md  design.md  tasks.md  specs/<capability>/spec.md   # ADDED/MODIFIED/REMOVED
```

`store-reporte` y `exportacion` especifican lo que **ya existe**, y eso no es
burocracia: hoy sus invariantes (coalescing por microtask; rehidratación
durante la evaluación del script y **no** en `load`; que la exportación
clone el DOM vivo) viven solo en comentarios dentro del archivo, y una IA que
no los lea los rompe.

**Se rechaza explícitamente una capacidad por cliente.**
`capabilities/cliente-novaventa` reintroduciría el fork a nivel de
especificación. Los clientes son **instancias** que viven en `perfiles/` y se
validan con pruebas de conformidad. Si un cliente necesita spec propia, es
señal de que una capacidad está mal delimitada.

**Los cuatro mecanismos que impiden que varias IAs se desvíen:**
1. **La spec es la puerta de revisión, no el diff.** Un PR que cambia
   comportamiento descrito en `specs/` sin su delta en `changes/*/specs/`
   **se rechaza sin leer el código**. Convierte "esto no era lo acordado" de
   opinión en hecho verificable.
2. **Conjuntos de archivos disjuntos.** El `tasks.md` de cada change lista
   los archivos que tocará, y **dos changes abiertos no pueden listar el
   mismo archivo**. Con el 49 % de los commits sobre un solo archivo, esta
   es la regla operativa que evita tres conflictos irresolubles
   simultáneos. En la práctica serializa F1–F5 sobre el HTML, y eso es
   correcto: ya son secuenciales por dependencia.
3. **Todo requisito es `SHALL` + al menos un `#### Scenario:`, y todo
   escenario debe ser expresable como aserción** en `REPORTE.autopruebas` o
   `pytest`. Si no se puede convertir en aserción no es un requisito, es un
   deseo, y se va a `design.md`.
4. **`project.md` abre con las tres restricciones inviolables**, como
   prohibiciones y con el motivo: **un archivo HTML abierto con `file://`**
   · **AF no cambia ni una cifra** · **Python stdlib + openpyxl**. Sin
   esto, la deriva más probable de un agente es *"esto sería más limpio con
   Vite/React/un servidor local"* — tendría razón en abstracto y estaría
   destruyendo el producto.

Un change no se archiva hasta que la verificación A/B contra `main` con
insumos reales dé **cero diferencias**.

---

## Fases, con criterio de aceptación verificable

La migración es *strangler fig* **dentro del archivo**: por cada mecanismo,
tres tiempos — (a) se introduce inerte, (b) el camino viejo **delega** en el
nuevo → A/B en 0, (c) se borra el camino viejo → A/B en 0. **Nunca conviven
los dos caminos más de un commit**; un camino viejo que "se queda por si
acaso" es el que produce el bug de dos verdades.

| Fase | Contenido | Criterio de aceptación |
|---|---|---|
| **F0** | Fundación: renombre a `InformeGerencialSETI`; `openspec/` + `project.md` + `AGENTS.md`; recuperar el inventario de tarjetas del PR #1 a `docs/`; **arnés `automatizacion/verificar_ab.py`** + goldens de AF | `verificar_ab.py` da 0 diferencias contra `main` con los insumos reales de junio-2026 **y detecta un cambio numérico introducido a propósito** (un arnés que nunca ha fallado no ha demostrado nada) |
| **F1** | Perfil AF extraído; `resolverPerfil` + reutilización de `fusionarProfundo`; claves de almacén con prefijo | 0 diferencias A/B; cero literales "Acción Fiduciaria" fuera de `perfiles/accion-fiduciaria.js` y la tabla de textos; las claves viejas de localStorage/IndexedDB se siguen leyendo |
| **F2** | Contrato desacoplado del DOM | 0 lecturas de `[data-k="finicio"]` en el pipeline (hoy 6); desaparece el fallback `new Date(2025,8,1)`; sin `contrato.inicio` el arranque **falla con mensaje**; A/B en 0 |
| **F3** | Descriptores de las 10 tarjetas **conviviendo** con el HTML a mano + autoprueba descriptor↔DOM; `criteriosCarga`/`EXTENSIONES_INSUMO`/`DOMINIOS`/`renderAll` derivados | La lista derivada produce **los mismos 7 criterios, en el mismo orden, con los mismos textos exactos**; A/B en 0 |
| **F4** | HTML de tarjetas generado desde plantilla única; modal de selección; preset persistido | Deseleccionar «Bolsa de horas» retira su criterio y su página del PDF y el resto de cifras es idéntico; volver a seleccionarla restaura el export **byte a byte**; PDF correcto con preset mínimo (1 tarjeta) y máximo |
| **F5** | Adaptadores + modelo canónico + fuentes alternativas con precedencia; AF migrado | A/B en 0; autoprueba que demuestra que `slaCumplido:null` **no** se cuenta como cumplido; encabezado ambiguo publica `invalido` con los candidatos |
| **F6** | Perfil Novaventa (AlertOps + `Data_<mes>` como alternativa) | Las cifras cuadran con `Novaventa/Informe Novaventa Junio 2026.pptx`; goldens de AF en 0; sobrescribe <30 % de las claves de AF; **cero funciones nuevas** salvo `bloque-con-fechas` y la tarjeta `capacidad` |
| **F7** | Adaptador Aranda (carga manual) + perfil Bancóldex | Los casos de junio-2026 cuadran con `Bancoldex/reporte-bancoldex-2026-07-02.pdf`; goldens de AF y Novaventa en 0; `cambio` y `ambiente` existen en el canónico **sin aparecer** en el informe de AF |
| **F8** | Automatización multicliente: `--cliente`, `.env.<cliente>` con precedencia sobre `.env` común, `insumos.py` genérico, ledger con dimensión de cliente | `actualizar_informe.py --cliente accion-fiduciaria` produce **el mismo sha256 por fuente** que la corrida previa; el ledger migrado conserva los periodos de AF; `pytest` verde |
| **F9** | Reglas compartidas JS↔Python (`reglas/casos.json` + hash) | La autoprueba falla si el hash de la tabla embebida no coincide — se verifica desincronizándola a propósito |
| **F10** | *(Opcional)* Split `fuente/` + `construir_informe.py` | Reproduce el HTML vigente **byte a byte** antes de aceptar el split |
| **F11** | Cardio Infantil | **Bloqueada** hasta resolver por sondeo las 4 preguntas abiertas del inventario. `clasificar_caso_cardio` conserva su `NotImplementedError` hasta entonces |

Cada fase: un `change` de OpenSpec archivado y un `docs/AAAA-MM-DD-tema.md`
con las secciones fijas del equipo (*Contexto / Qué se implementó /
Verificación realizada / Archivos tocados / Pendiente*).

### Notas sobre dos fases delicadas

**F3 antes que F4, y no al revés.** Los `slideCard` están ocultos por CSS
(línea 4593) pero **siguen siendo el destino de escritura de los parsers**
(`document.querySelector('#s4 tbody tr…')`) y el nodo que captura
html2canvas. Por eso: primero se declara el descriptor junto al HTML a mano,
después una autoprueba demuestra que el modelo describe la realidad (id,
título, dominios, texto del criterio, `exportable`), y **solo entonces** el
HTML se genera desde el descriptor. Es *reconocimiento antes que
construcción* aplicado a un refactor.

**F10 llega tarde a propósito.** A favor del split: 49 % de commits en un
archivo, 555 KB de lógica propia, conflictos garantizados con varias IAs. En
contra, y pesa más: el valor entero del artefacto es que se abre con doble
clic; un build significa que **lo que revisas no es lo que entregas**; y
**ya hay un build implícito** (`exportarHTML()` clona el DOM vivo).
Decisión: **nada de bundler**, un concatenador en Python stdlib guiado por
marcadores `<!-- @incluir ruta -->`, sin transpilar ni minificar, cada byte
de salida rastreable a un byte de entrada. Y después de F1–F5, cuando los
cortes ya sean evidentes: partir antes solo traslada el monolito a carpetas.
El vendor (87 % del peso: Chart.js, SheetJS, jsPDF, fuentes base64) se
congela como blob y nunca se toca — eso ya elimina la mayoría del ruido de
diffs sin ningún build.

---

## Archivos críticos

- `informe-accion-fiduciaria 1.html` — el monolito. Puntos de anclaje:
  `DOMINIOS` (1588), `REPORTE` (1591), `criteriosCarga` (1674),
  `filaCabecera` (1882), `autopruebas` (2015), parsers (2776–3990),
  `exportarHTML` (4431), `fusionarProfundo` (4817), `montarHistorico`
  (4932), `montarRadarCI` (6032), `renderAll` (6170)
- `automatizacion/insumos_af.py` — contrato de datos + reglas compartidas;
  se vuelve `insumos.py` parametrizado por perfil
- `automatizacion/historico_casos.py` — ledger sin dimensión de cliente;
  **la migración de datos de mayor riesgo**
- `automatizacion/extraer_indisponibilidades.py:73` — `CLIENTE_OBJETIVO`
  hardcodeado sobre un archivo compartido entre AF, Bancóldex y EMI
- `automatizacion/test_insumos_af.py` — toda la cobertura de Python que
  existe hoy (54 líneas, solo `clasificar_caso_glpi`)

---

## Verificación

**Arnés A/B (`automatizacion/verificar_ab.py`, stdlib puro).** Toma dos HTML
**exportados** (uno de `main`, uno de la rama), extrae `window.__ESTADO__`
con regex + `json.loads` (el mismo truco que `insumos_af.py` ya usa con
`_PATRON`), y con `html.parser` el texto normalizado de todo
`.tarjeta-kpi__valor`, `.tarjeta-kpi__meta`, `.tarjeta-kpi__chip`, celdas de
tabla y `.dashboard-detail`. Diff estructurado. **Sobre el exportado y no
sobre el store**, porque `exportarHTML()` clona el DOM vivo: hay textos que
existen solo en el DOM, y un diff del store no los vería.

**`REPORTE.autopruebas` pasa de función plana a suites**, conservando
**textualmente** las ~47 aserciones actuales: `nucleo` (invariantes del
store) · `perfil` (conformidad: cada tarjeta resuelve, cada estrategia
existe, ningún `'@heredado:borrar'` colgando, métrica anti-fork) · `reglas`
(tabla compartida por cliente) · `tarjetas` **parametrizada por descriptor**
· `conArchivos` (concordancia tarjeta↔modal↔store con selectores del
descriptor).

> La suite `tarjetas` es la de mayor apalancamiento: para **cada** tarjeta
> seleccionada, con el store vacío, ningún `%`, ningún chip "Cumple",
> criterio en `false`. Hoy esas tres aserciones están escritas una vez sobre
> selectores fijos; parametrizadas **cubren gratis toda tarjeta futura de
> todo cliente futuro**. Es exactamente la clase de bug que persiguió toda
> la auditoría del 02/08.

Nuevo: `await REPORTE.autopruebas({perfil:'novaventa'})` intercambia el
perfil, corre en frío y restaura en `finally` — misma disciplina que ya usa
el bloque de `RECONCILIACION_INDISPONIBILIDADES`.

**Deuda de Python, por orden de riesgo:** (1) empaquetado — el upsert no
pierde el archivo del otro extractor, sha256, y `fijar_periodo` con **mes
0-based** (ese desfase por uno morderá con cuatro clientes); (2)
`historico_casos` con dimensión de cliente — *escribir junio de Novaventa no
puede tocar junio de AF*, la prueba de regresión de la migración escrita
antes de hacerla; (3) `extraer_indisponibilidades` con fixture de clientes
mezclados (la situación real); (4) adaptadores con fixtures dorados.

**Fixtures — sintéticos, no reales.** El commit `ab9176a` ya sacó datos de
cliente del repo una vez. Los fixtures llevan nombres de columna y strings de
categoría **reales**, con IDs, títulos y contenido **inventados**.
`Bancoldex/` y `Novaventa/` van a `.gitignore`.

**Goldens por cliente y periodo** (`dorados/<cliente>-<AAAA-MM>.json`).
**Regla de merge: ningún perfil nuevo entra si las goldens de todos los
perfiles existentes no pasan sin cambios.** Ventaja concreta: los
entregables reales ya están en el árbol para validar contra la verdad, no
contra sí mismos — el `.pptx` de Novaventa y el `.pdf` de Bancóldex son la
referencia de lo que el cliente ya recibió.

Un solo comando: `verificar` = `pytest` + `verificar_ab.py` sobre todas las
goldens.

---

## Riesgos, por daño esperado

1. **Regresión silenciosa en AF** — rompe el criterio de aceptación
   central. `exportarHTML()` clona el DOM vivo, así que un cambio de
   plantilla puede alterar un texto sin que ninguna prueba de store lo
   note. → La golden se toma sobre el **HTML exportado**, la única captura
   que ve lo mismo que el cliente.
2. **El encabezado ambiguo de Novaventa produce un número plausible y
   falso** — metas entregadas como resultados. → Regla "más de un
   candidato ⇒ `invalido`" + autoprueba con la hoja real verificando que el
   bloque elegido es f7–f10.
3. **La herencia degenera en fork** — no es hipotético: `insumos_cardio.py`
   ya existió con 244 líneas duplicadas. → Métrica del 30 % como
   autoprueba; prohibición explícita en `project.md`; F8 **borra**, no deja
   "por ahora".
4. **Deriva JS↔Python de las reglas** — con 4 clientes serían 8
   implementaciones. → Tabla compartida + hash. *Siguen siendo dos
   implementaciones; lo que se elimina es la divergencia silenciosa.*
5. **Varias IAs colisionando en un archivo de 6 525 líneas** → conjuntos de
   archivos disjuntos por change, que serializa F1–F5 sobre el HTML
   (correcto: ya son secuenciales).
6. **PDF y html2canvas con tarjetas dinámicas** — la captura depende de
   nodos concretos y de un ajuste iterativo al marco 16:9. → `exportable`
   en el descriptor + autoprueba de páginas = tarjetas exportables +
   portada + prueba con preset mínimo y máximo en F4.
7. **`DisponibilidadMensual.xlsx` compartido entre AF, Bancóldex y EMI** —
   un cambio de filtro afecta dos informes, y el archivo se bloquea en vivo
   (commit `ea78db1`). → Fixture con las tres entidades mezcladas; **no
   relajar nunca el reintento por bloqueo** al refactorizar.
8. **Sobre-diseño: el informe se vuelve un motor genérico que nadie sabe
   operar.** Riesgo alto justo porque el diseño es bueno sobre el papel. →
   La regla dura de "dos clientes con evidencia real" antes de cualquier
   mecanismo nuevo.
9. **Reintroducir datos reales de cliente al repo** → fixtures sintéticos,
   `.gitignore`, revisión de `git diff --stat` antes de cada merge de fase.
10. **Cardio Infantil sin fuentes confirmadas** — 4 de 8 tarjetas en 🔴,
    Zabbix es candidato no hecho. → No se le abre perfil hasta tener insumo
    confirmado. El `NotImplementedError` deliberado de
    `clasificar_caso_cardio` es la actitud correcta y se conserva tal cual.

---

## Preguntas abiertas (no bloquean; se resuelven por sondeo, no por inferencia)

- ¿Aranda (Bancóldex) expone API? Hoy se asume export manual.
- ¿Cuál fecha de GLPI cuenta contractualmente para SLA? Es el pendiente de
  negocio más antiguo del proyecto.
- Bancóldex: la hoja `TYA` (86 filas con `Integrante | Actividad | Horas
  Reportadas`) podría **automatizar la bolsa de horas**, que en AF es 100 %
  manual por diseño. Candidata a tarjeta/mecanismo nuevo — pero solo si un
  segundo cliente la necesita.
- Cardio: entidad GLPI, equivalente de `Revisión Alerta`, `searchOptions`
  reales, y si Zabbix expone disponibilidad/backups.

---

## Estado de ejecución

**Nota operativa (04/08/2026):** el plan se ejecutó con varias IAs en
paralelo desde el inicio, tal como preveía este documento — la mayor parte
de F0 no se hizo en la rama `refactor/multicliente-f0-fundacion` sino en
ramas hermanas, cada una con su PR propio, revisadas y mergeadas a `main`
por separado. Esta rama terminó aportando solo el propio plan y un ajuste
de `.gitignore`. Quien retome el trabajo: la fuente de verdad es siempre
`main`, no esta rama.

| Fase | Estado |
|---|---|
| F0 | **Casi completo.** Renombre del repo a `InformeGerencialSETI` (hecho) · `openspec/project.md` + `AGENTS.md` (PR #11, mergeado) · inventario de tarjetas recuperado a `docs/` (PR #7, mergeado) · arnés `automatizacion/verificar_ab.py` (PR #10, mergeado) · mecanismo de dorados sin datos en claro (PR #14, mergeado). **Pendiente externo:** correrlo contra un export real completo de AF con insumos de junio-2026 y crear `dorados/accion-fiduciaria-2026-06.json`. Sin esa evidencia, el criterio de aceptación exacto de F0 no está cerrado. |
| F1 | **Completada y fusionada en `main` (PR #12).** Perfil de datos, `resolverPerfil()`, `fusionarProfundo` global, `REPORTE.cliente`, filtros, claves de almacén y textos de interfaz migrados; la resolución del conflicto combina correctamente claves nuevas/viejas con herencia de bolsa entre periodos. El export transporta el perfil resuelto sin depender de `perfiles/`, y la capacidad `perfil-cliente` tiene change, spec y pruebas. El 04/08/2026 se generaron exportaciones de `main` (`6ee842d`) y la rama (`c536853`) con los mismos cuatro insumos reales completos de julio de 2026: los siete criterios validaron y `python3 automatizacion/verificar_ab.py /tmp/export-main-julio-2026.html /tmp/export-pr12-julio-2026.html` informó **0 diferencias**. Los insumos y exports permanecen fuera del repositorio. |
| F2 | **Completada técnicamente.** El inicio contractual se movió de las seis lecturas del DOM a `PERFIL.contrato.inicio` y se valida sin fallback. El 05/08/2026 se compararon dos exportaciones reales completas — `main` `404408c` y esta rama — con el mismo paquete `automatizacion/salida/insumos-af.js`, que incluye `indisponibilidades-2026-07.csv`, y los mismos insumos manuales de Acción Fiduciaria: `verificar_ab.py` informó **0 diferencias**. |
| F3 | **Completada.** El perfil declara las diez tarjetas actuales y un inventario del motor deriva dominios, extensiones, criterios y renderizadores. La conformidad descriptor↔DOM está cubierta en `REPORTE.autopruebas` y `unittest`. El 05/08/2026, las exportaciones completas reales `export-main-f3.html` (`main` `404408c`) y `export-f3.html` (`a0b0fdb`) se cotejaron con `automatizacion/verificar_ab.py`: **0 diferencias**. |
| F4 | **Completada.** El panel se genera desde la presentación declarativa del inventario, el selector persiste por perfil y el PDF/exportado usan la selección efectiva. El 05/08/2026, `export-main-f3.html` y `export-f4.html` dieron **0 diferencias**; el usuario verificó después el PDF con selección reducida y con el preset predeterminado restaurado. |
| F5–F11 | Pendientes |
