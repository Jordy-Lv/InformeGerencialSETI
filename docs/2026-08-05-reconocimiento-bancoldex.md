# Reconocimiento de Bancoldex para el adaptador Aranda (F7)

**Fecha:** 5 de agosto de 2026

## Contexto

La prioridad solicitada es que el informe pueda interpretar los datos de
Bancoldex. Antes de implementar, se revisaron las restricciones del proyecto,
las especificaciones OpenSpec vigentes, el plan multicliente, el motor HTML,
la automatización existente y los cuatro insumos reales ignorados por Git en
`Bancoldex/`.

Este documento registra el reconocimiento. **No cambia el comportamiento del
informe ni crea un perfil Bancoldex todavía.** Por tanto no requiere un delta
OpenSpec: los requisitos de las capacidades `adaptadores-fuente`, inventario
de tarjetas y perfil Bancoldex se escribirán en su change correspondiente
antes de tocar el motor.

La fase prevista para este trabajo es F7: adaptador Aranda de carga manual y
perfil Bancoldex. F3 a F5 son prerrequisitos deliberados de F7: descriptores
de tarjetas, tarjetas configurables y modelo canónico/adaptadores. Saltarlos
forzaría ramas por cliente dentro del HTML y violaría el principio de
multicliente por configuración.

## Fuentes reconocidas

Los insumos reales permanecen ignorados por `.gitignore`; este documento no
reproduce identificadores de casos, textos de usuarios ni contenido de los
registros.

| Fuente | Estructura relevante | Uso esperado |
|---|---|---|
| `Casos  + tareas BD junio 2026.xlsx` | Hoja `Junio`, una fila de cabecera y 72 filas. Incluye `TIPO_DE_CASO`, `NUMERO_DEL_CASO`, `JERARQUIA`, `MOTOR`, `INDICARDOR DE CUMPLIMIENTO` y `FECHA_REGISTRO`. | Casos de Aranda, SLA, tipo, jerarquía y motor. |
| `Data consolidada junio_Bancoldex 2026.xlsx` | Hojas `Linea Base`, `Ejecucion Backups`, `Indicador`, `Casos` y `Disponibilidad Real`. | Línea base, indicadores, backups, históricos y disponibilidad por motor. |
| `Logros_Mitigacion_TYA Bencoldex_junio.xlsx` | Hojas `Logros`, `Mitigación` y `TYA`. | Contenido cualitativo del periodo; `TYA` es una sábana de horas y no debe suponerse compatible con la tarjeta de bolsa sin una regla explícita. |
| `reporte-bancoldex-2026-07-02.pdf` | Informe de junio de 2026, 11 páginas. | Referencia externa para validar el perfil Bancoldex, no fuente de cálculo. |

## Hallazgos verificables de los insumos

### Casos de Aranda

La hoja `Junio` contiene 72 registros fechados íntegramente entre el 1 y el
30 de junio de 2026. Sus agregados coinciden con las gráficas del PDF de
referencia:

| Métrica | Resultado |
|---|---:|
| Casos totales | 72 |
| Incidente - Monitoreo | 33 |
| Requerimiento | 32 |
| Tarea | 5 |
| Incidente | 2 |
| Oracle | 52 |
| SQL Server | 19 |
| WebLogic | 1 |
| SLA `Cumple` | 71 |
| SLA `No cumple` | 1 |

El tipo debe derivarse de `TIPO_DE_CASO`, no de la jerarquía como ocurre en
GLPI. La jerarquía usa `.` como separador (`Base De Datos.Intermiencia`), no
`>`.

### Identidad del cliente: la regla propuesta inicialmente es incorrecta

El plan inicial propuso filtrar Aranda con `Proyecto` que contenga
`Bancoldex`. La evidencia real la contradice:

- Las 72 filas tienen `Proyecto = Mesa de Servicios TI.`.
- `COMPANIA = BANCOLDEX` aparece solo en 64 filas.
- Las 8 filas restantes no tienen compañía, pero el PDF de Bancoldex las
  incluye en sus totales de 72.

Por ello, filtrar por `Proyecto` produciría cero casos y filtrar por
`COMPANIA` perdería ocho. El adaptador no puede codificar ninguno de esos
filtros como si fuera una garantía de la fuente.

La decisión que debe quedar escrita en el diseño de F7 es una de estas dos:

1. **Archivo de alcance único:** el perfil Bancoldex acepta todas las filas
   porque el export se entrega específicamente para Bancoldex; la identidad
   se valida por el perfil seleccionado y por el esquema, no por una columna.
2. **Archivo de alcance mixto:** se requiere una columna o regla de Aranda
   que identifique las 72 filas sin excluir las ocho vacías; debe comprobarse
   contra otra exportación real antes de implementarla.

No se debe inventar una tercera condición a partir de `Asunto`, descripciones
o identificadores de infraestructura: eso convertiría textos operativos en
un filtro no auditable.

### Consolidado

Bancoldex no usa el esquema de Acción Fiduciaria:

- `Indicador` tiene cuatro métricas, no tres, y su cabecera ocupa dos filas:
  la primera aporta el mes y la segunda distingue las series `BANCOLDEX` y
  `SETI`.
- La meta de disponibilidad es 99,98 %, no 99,30 %.
- `Ejecucion Backups` identifica las filas por `BD`, no por `Instancias`.
- `Linea Base` agrega `AMBIENTE`, además de CI y motor.
- `Disponibilidad Real` publica disponibilidad por motor y no las dos tablas
  `Disponibilidad Real` / `Disponibilidad SETI` de la hoja esperada hoy por
  Acción Fiduciaria.
- La hoja `Casos` conserva un histórico con el tipo adicional `Cambio`, pero
  no sustituye el export Aranda del periodo para calcular los 72 casos.

Estos cambios justifican las estrategias declaradas en el plan: cabecera de
dos filas, adaptador Aranda y los campos canónicos opcionales `motor`,
`ambiente` y `cambio`. Esos campos no deben aparecer en Acción Fiduciaria
solo porque existan para Bancoldex.

### Contenido cualitativo

El archivo mensual tiene cinco filas de `Logros` y dos de `Mitigación`; sus
encabezados no son el registro mensual de Acción Fiduciaria. El perfil deberá
declarar esta variante de entrada o el lector genérico deberá reconocerla por
encabezados, con una prueba sintética. La hoja `TYA` contiene 86 filas y no
establece, por sí sola, cómo debe calcularse o mostrarse la bolsa de horas.

## Comportamiento actual comprobado

Se abrió el HTML actual en una sesión local de navegador, se seleccionó
junio de 2026 y se cargaron los insumos mediante los mismos controles de
archivo que usa una persona. No se guardó ni exportó ningún informe.

1. Al cargar el consolidado Bancoldex, el informe lo marca como incompleto.
   El motor exige las hojas `Indicadores`, `Disponibilidad` y `Backups`; no
   reconoce los nombres ni las formas de Bancoldex.
2. Al cargar el export Aranda por la entrada que hoy recibe GLPI, el informe
   lo rechaza correctamente: exige `Entidad`, `Fecha de apertura` y
   `Categoría/Tipo`, que no existen en la fuente Aranda.
3. La validación no produjo cifras Bancoldex falsas. El informe conserva el
   estado explícito de error y bloquea la exportación, que es el
   comportamiento seguro mientras F7 no exista.

Esto confirma que el problema no se resuelve renombrando archivos: se necesita
un adaptador registrado y un perfil con declaraciones de fuente propias.

## Diseño mínimo que deberá materializar F7

El change de F7 deberá especificar, probar y documentar como mínimo:

1. Un perfil `bancoldex` de datos puros que extienda `base`, no Acción
   Fiduciaria. El delta de estructuras es demasiado grande para una herencia
   útil de Acción Fiduciaria.
2. Un adaptador `aranda-export` de carga manual que mapee las columnas reales
   del export a `CasoCanonico` y use la estrategia
   `aranda-por-tipo-de-caso`.
3. Una estrategia de SLA de tres valores: `Cumple` → `true`, `No cumple` →
   `false`, vacío o valor desconocido → `null`.
4. La decisión explícita de alcance de cliente descrita arriba. Si se usa
   archivo de alcance único, un archivo ambiguo o de varios clientes debe
   fallar visible y verificablemente, no mezclarse de forma silenciosa.
5. Lectores de consolidado declarados por perfil: cabecera de dos filas de
   indicadores, backups por `BD`, disponibilidad por motor y línea base con
   ambiente.
6. Fixtures sintéticos que reproduzcan los nombres de columna, los dos
   valores de SLA y las ocho filas sin compañía, sin versionar datos reales.
7. Comparación contra el PDF de junio de 2026: los totales por tipo y motor
   deben coincidir; las referencias existentes de Acción Fiduciaria y las de
   cualquier perfil ya incorporado deben seguir sin diferencias.

## Secuencia y coordinación

El árbol de trabajo tiene un change F2 activo que ya lista
`informe-accion-fiduciaria 1.html` y `docs/2026-08-04-plan-multicliente.md`.
La regla de OpenSpec prohíbe que otro change abierto reserve esos mismos
archivos. Por eso este reconocimiento no modifica el plan maestro ni el HTML.

La ruta segura para priorizar Bancoldex es:

1. Cerrar y aislar F2.
2. Ejecutar F3, F4 y F5 manteniendo equivalencia A/B de Acción Fiduciaria.
3. Abrir F7 con el contrato anterior y los fixtures sintéticos.
4. Validar F7 contra los cuatro insumos reales ignorados y el PDF de junio.

## Verificación realizada

- Inventario de fuentes reales: `find Bancoldex -maxdepth 2 -type f` confirmó
  los cuatro insumos declarados en este documento.
- Estructura de Excel y agregados: lectura de libros con `openpyxl` en modo
  de solo lectura; se inspeccionaron hojas, encabezados, periodos y conteos.
- PDF: se renderizaron y revisaron visualmente sus 11 páginas; las páginas de
  indicadores, casos por tipo, casos por motor y backups se contrastaron con
  los agregados del export.
- Prueba de integración local del HTML: carga del consolidado y del export
  Aranda por los controles reales; ambos rechazos descritos arriba fueron
  visibles en el Centro de carga mensual.
- Suite actual: `python3 -m unittest discover -s automatizacion -p
  'test_*.py' -v` → `Ran 40 tests ... OK`.
- Arnés de exportación: `python3 automatizacion/verificar_ab.py --autoprueba`
  → `Autoprueba OK`.

## Archivos tocados

- `docs/2026-08-05-reconocimiento-bancoldex.md` (este documento).

## Pendiente

- Confirmar si el export Aranda se entrega siempre con alcance exclusivo de
  Bancoldex. Sin esa decisión no hay un filtro de cliente seguro.
- Completar las fases F3 a F5 antes de implementar el perfil y adaptador F7.
- Escribir el change de F7 con propuesta, diseño, tareas, delta de spec y
  fixtures sintéticos antes de editar el motor.
- Actualizar el estado de ejecución del plan maestro cuando F2 ya no reserve
  ese archivo.
