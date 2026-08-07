# Informe Gerencial SETI — restricciones del proyecto

Este documento es la primera pantalla que cualquiera (persona o IA) debe leer
antes de tocar este repositorio. Lo que sigue no son preferencias de estilo:
son restricciones que, si se rompen, destruyen el producto o reintroducen un
problema ya resuelto con evidencia real.

## Las tres restricciones inviolables

### 1. Un archivo HTML abierto con `file://`

El informe **no** depende de un servidor, de una build, ni de conexión a
internet. Se abre con doble clic. Esto es la razón por la que:

- No hay bundler, no hay `npm run build`, no hay transpilación.
- No hay ninguna llamada de red desde el HTML (`fetch` a algo que no sea un
  archivo vecino en `file://` está prohibido).
- Cualquier propuesta de "esto sería más limpio con Vite/React/un servidor
  local" tiene razón en abstracto y está destruyendo el producto. Se
  rechaza, sin excepción, sin importar cuánto mejore la arquitectura.

**Motivo:** el valor entero del artefacto para el cliente es que se abre y
funciona, sin instalar nada. Un build significa que lo que se revisa no es
lo que se entrega.

### 2. Acción Fiduciaria no cambia ni una cifra

Ninguna fase de la migración a plataforma multicliente puede alterar una
sola cifra, texto o comportamiento visible del informe de Acción Fiduciaria.
El criterio de aceptación de cada fase que toque el HTML es **0 diferencias**
contra `main`, verificado con `automatizacion/verificar_ab.py` sobre el HTML
**exportado** (no sobre el store en frío — `exportarHTML()` clona el DOM vivo
e incrusta el estado ya resuelto; hay texto que solo existe en esa copia).

**Motivo:** es un producto en producción, para un cliente real, que se
entrega cada mes. Una regresión silenciosa no es un bug de desarrollo: es un
número incorrecto que alguien de SETI podría entregarle a Acción Fiduciaria
sin saberlo.

### 3. Python: solo librería estándar, más `openpyxl` donde ya se usa

`automatizacion/` no introduce dependencias nuevas. La única excepción ya
existente es `openpyxl`, y solo para lo que ya la necesita
(`extraer_indisponibilidades.py`, que lee un `.xlsx` real con celdas
combinadas y tipos mixtos).

**Motivo:** estos scripts terminan corriendo en un servidor desatendido
(tarea programada) donde instalar dependencias es fricción y superficie de
falla adicional. Ver `requirements.txt`.

## El principio rector: dónde se corta la línea entre dato y código

Es la regla que decide todo lo demás en el diseño multicliente, y está
redactada para ser decidible sin discusión:

> **Es dato** si al cambiarlo solo cambian números, etiquetas o rutas que un
> algoritmo existente ya sabe procesar.
> **Es código (estrategia registrada)** si al cambiarlo cambia *cómo se
> decide algo* o *cómo se recorre una estructura*.
> **Prueba práctica:** ¿podrías revisarlo con el líder de cuenta sin
> explicarle qué es una función? Sí → dato. No → estrategia.

Ejemplos ya decididos con evidencia real:

- **Dato:** meta de disponibilidad (0,993 vs 0,99 vs 0,9998) · nombre de
  hoja del consolidado · separador de jerarquía de categorías (`>` vs `.`) ·
  entidad GLPI · lista de CI y motores · orden y selección de tarjetas.
- **Código (estrategia con nombre):** clasificar casos por categoría (Acción
  Fiduciaria / Novaventa) vs por `TIPO_DE_CASO` (Bancóldex) · detección de
  encabezado (primera fila vs bloque con fechas vs cabecera de dos filas) ·
  de dónde sale el SLA (columna "Tiempo para resolver excedido" vs
  `INDICARDOR DE CUMPLIMIENTO`).

**Corolario duro:** ningún mecanismo nuevo (campo del modelo canónico,
estrategia registrada, tipo de componente) se acepta sin **dos clientes con
evidencia real** que lo necesiten. Si solo un cliente necesita algo, es un
campo opcional del modelo canónico — no una dimensión de primera clase que
todos los clientes vean en la interfaz.

## Multicliente por configuración, no por copia

**Se prohíbe crear árboles de código por cliente.** Concretamente:

- Ningún archivo `insumos_<cliente>.py`, `extraer_<cliente>.py`, ni carpeta
  `<cliente>/automatizacion/`.
- Ningún archivo `informe-<cliente>.html` con lógica propia — hay **un**
  motor (`informe.html`, la plantilla), y lo que varía entre clientes vive
  en `perfiles/<cliente>.js` (datos, sin funciones) y en las salidas
  generadas (`informe-<cliente>-<periodo>.html`).
- Un perfil de cliente es un objeto serializable a JSON. **No contiene
  funciones.** Cuando necesita comportamiento, nombra una estrategia
  registrada por string. Un string que no resuelve falla al arrancar, con
  la lista de nombres desconocidos — una función mal escrita falla más
  tarde, ya con un número pintado en pantalla.

Esto ya se probó una vez en sentido contrario: el PR #5 intentó sumar un
cliente nuevo copiando `automatizacion/` completo (11 de 13 funciones
duplicadas). Se cerró sin mergear — ver el historial de PRs #5–#10 para el
razonamiento completo.

## Dónde vive cada cosa

| Qué | Dónde |
|---|---|
| El motor (plantilla) | `informe.html` |
| Perfiles de cliente (datos) | `perfiles/<cliente>.js` |
| Estrategias registradas (código) | dentro del motor, por registro con nombre |
| Automatización de insumos, compartida | `automatizacion/` |
| Verificación | `automatizacion/verificar_ab.py`, `pytest`, `REPORTE.autopruebas` |
| Especificación de comportamiento | `openspec/specs/<capability>/spec.md` |
| Propuestas de cambio en curso | `openspec/changes/<fecha>-<id>/` |
| Historial narrado de cada sesión de trabajo | `docs/<fecha>-<tema>.md` |

## Flujo de trabajo (ramas y PR)

Se trabaja en ramas independientes, con PR contra `main`, revisadas por
alguien distinto de quien las abrió (`main` tiene protección de rama que lo
exige — el autor de un PR no puede aprobar el suyo propio). Ver
`openspec/AGENTS.md` para el detalle de cómo se estructura un `change` de
OpenSpec y qué evita que varias IAs trabajando en paralelo se pisen.
