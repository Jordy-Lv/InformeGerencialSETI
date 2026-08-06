# Patrones de diseño del proyecto

Las decisiones de arquitectura, con el motivo de cada una y las alternativas
descartadas **con nombre**. Extraído de la sección 4 del
[plan maestro](2026-08-04-plan-multicliente.md), donde estaba mezclado con el
cronograma de fases y era imposible de citar en una revisión.

Un patrón aquí no es una preferencia: es una respuesta a un problema concreto
que este repositorio ya tuvo. Si vas a apartarte de uno, di de cuál y por qué.

---

## La regla que decide antes que cualquier patrón

> **Es dato** si al cambiarlo solo cambian números, etiquetas o rutas que un
> algoritmo existente ya sabe procesar.
> **Es código (estrategia registrada)** si al cambiarlo cambia *cómo se
> decide algo* o *cómo se recorre una estructura*.
> **Prueba práctica:** ¿podrías revisarlo con el líder de cuenta sin
> explicarle qué es una función? Sí → dato. No → estrategia.

Ejemplos ya decididos con evidencia real:

- **Dato:** meta de disponibilidad (0,993 · 0,99 · 0,9998) · nombre de hoja
  del consolidado · separador de jerarquía de categorías (`>` vs `.`) ·
  entidad GLPI · lista de CI y motores · orden y selección de tarjetas.
- **Código (estrategia con nombre):** clasificar casos por categoría (Acción
  Fiduciaria, Novaventa) vs por `TIPO_DE_CASO` (Bancóldex) vs por hoja de
  origen (Cardio Infantil) · detección de encabezado (primera fila vs bloque
  con fechas vs cabecera de dos filas) · de dónde sale el SLA (columna
  «Tiempo para resolver excedido» vs `INDICARDOR DE CUMPLIMIENTO`).

**Corolario duro:** ningún mecanismo nuevo se acepta sin **dos clientes con
evidencia real** que lo necesiten. Con uno solo es un campo opcional del
modelo canónico, no una dimensión de primera clase.

---

## 1. Registry — para tarjetas y estrategias

Un registro por nombre, no un contenedor de inyección de dependencias: no hay
red (`file://`), no hay módulos, no hay ciclo de vida, y el registro debe
**sobrevivir al clonado del DOM** en `exportarHTML()`.

El beneficio que lo hace innegociable no es técnico sino de gobierno: las
claves del registro son **el vocabulario cerrado** que la spec restringe. Un
agente no puede inventar `clasificador: 'lo-que-se-me-ocurrió'` sin que el
arranque falle con la lista de nombres válidos.

## 2. Herencia por resolución de datos — no por clases

`resolverPerfil()` + `fusionarProfundo()`. **No** `class PerfilNovaventa
extends PerfilAF`.

Una jerarquía de clases invita a sobrescribir métodos, y sobrescribir métodos
es exactamente el camino que produjo `insumos_cardio.py` en el PR #5.
Descartado también **Builder**: rompería la serialización del perfil a JSON,
que es lo que permite transportarlo dentro del export.

## 3. Strategy nombrada por string — clasificación, cabecera y SLA

Contra **Template Method**, que obliga a una jerarquía de clases y hace
imposible responder desde los datos la pregunta *«¿qué gancho sobrescribió
cada cliente?»* — justo la pregunta de auditoría de este proyecto.

Con Strategy, `grep clasificador: perfiles/` responde en una línea. Y el
camino de código de Acción Fiduciaria queda **literalmente intacto**.

## 4. Adapter + Modelo Canónico — el innegociable

Sin un modelo canónico, cada adaptador alimenta las tarjetas directamente y
las tarjetas se llenan de ramas por cliente: el mismo problema, un nivel más
arriba.

Es además **el único lugar donde «fallar ruidosamente» se puede
representar**. Un adaptador que no encuentra una columna produce un fallo
explícito en el canónico, no un cero que parece un dato.

## 5. Extender el Observer que ya existe (`REPORTE`) — y no meter una librería

Una decisión de **no** aplicar un patrón. `REPORTE` ya tiene agrupamiento por
microtarea y cinco estados explícitos por dominio; pasar de 2 a ~15
suscriptores sigue siendo trivial.

Un store tipo Redux reescribiría la única parte bien hecha del sistema,
contra la cual asertan las autopruebas embebidas. Está especificado en
[`openspec/specs/store-reporte/spec.md`](../openspec/specs/store-reporte/spec.md).

## 6. Anti-Corruption Layer en Python

`insumos.py` genérico parametrizado por perfil, más `perfiles/<cliente>.py`
solo con lo que difiere. Respuesta directa a `insumos_cardio.py`, y la razón
por la que `project.md` **prohíbe** crear archivos `insumos_<cliente>.py`.

## 7. Fuente única para las reglas compartidas JS↔Python (`reglas/casos.json`)

Hoy `clasificar_caso_glpi` está implementada dos veces y la tabla de casos
está duplicada a mano en `test_insumos_af.py` y en `REPORTE.autopruebas`. Con
cuatro clientes serían ocho tablas.

**Honestidad sobre su alcance:** esto **no unifica las dos
implementaciones** — transpilar violaría la restricción de stdlib. Elimina la
divergencia *silenciosa*, que es el 90 % del valor por el 10 % del costo.

---

## Descartados, con nombre y motivo

| Patrón | Por qué no |
|---|---|
| **Factory / Abstract Factory** | Sería un `switch` con ceremonia |
| **Decorator sobre tarjetas** | Volvería no evidente el orden del DOM, que es justo lo que `html2canvas` captura |
| **Command / Undo para el preset** | Ritual sobre un arreglo corto |
| **Event Bus aparte** | `REPORTE` ya es el bus. Dos canales, dos verdades |
| **Web Components** | Shadow DOM rompería `html2canvas` y el clonado de `exportarHTML()` |
| **Herencia de clases entre perfiles** | Invita a sobrescribir métodos (ver patrón 2) |
| **Builder de perfiles** | Rompe la serialización a JSON |
| **Store tipo Redux** | Reescribiría la parte del sistema mejor probada (ver patrón 5) |

---

## Patrones de proceso

No son de código, pero deciden más que varios de los anteriores.

### La spec es la puerta de revisión, no el diff

Un PR que cambia comportamiento descrito en `openspec/specs/` sin su delta
correspondiente **se rechaza sin leer el código**. Convierte «esto no era lo
acordado» de una opinión en un hecho verificable.

### Conjuntos de archivos disjuntos entre changes abiertos

El `tasks.md` de cada change declara una lista cerrada de archivos, y dos
changes abiertos no pueden declarar el mismo. Con un archivo de 6.700 líneas
concentrando la mitad de los commits, es lo que evita un conflicto
irresoluble entre dos agentes en paralelo.

En la práctica serializa las fases que tocan el HTML una detrás de otra — y
eso es correcto: ya son secuenciales por dependencia.

### Todo requisito es `SHALL` + al menos un escenario verificable

La prueba de que un requisito está bien escrito es que se pueda convertir
directamente en una aserción de `REPORTE.autopruebas` o de `pytest`. **Si no
se puede convertir en aserción, no es un requisito — es un deseo, y va a
`design.md`.**

### Reconocimiento antes que construcción

Si algo depende de una fuente externa (GLPI, AlertOps, Zabbix, Aranda), se
sondea primero y se confirma contra evidencia real. Por eso existen
`sonda_glpi.py` y `sonda_alertops.py` como scripts separados de los
extractores: no se asume que un identificador de campo es igual al de otro
cliente porque compartan plataforma.

### Verificación diferencial como criterio de aceptación

Para un producto en producción que no puede cambiar una cifra, la prueba
unitaria no alcanza. `verificar_ab.py` compara dos exports reales y exige
**cero diferencias**. Los dorados (`dorados/<cliente>-<AAAA-MM>.json`)
permiten versionar esa referencia como huellas SHA-256, sin publicar ni una
cifra del cliente.
