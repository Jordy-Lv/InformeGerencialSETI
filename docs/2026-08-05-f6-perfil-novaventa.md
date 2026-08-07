# F6 — Perfil Novaventa y gestión de capacidad

## Contexto

F6 incorpora Novaventa mediante herencia de Acción Fiduciaria. Los insumos
reales verificaron dos diferencias previas: indicadores con un bloque inicial
de metas sin fechas y `Data_<mes>` como alternativa de AlertOps. Quedaba
pendiente leer la ocupación de filesystems de la hoja `Capacidad` sin
reinterpretarla como la bolsa manual de horas de Acción Fiduciaria.

## Qué se implementó

- `perfiles/novaventa.js` declara `c10` junto con la fuente `Capacidad`.
- El motor publica `capacidad` con los filesystems, la ocupación por corte y
  la ocupación máxima; no escribe ni deriva datos en `bolsa`.
- Para Novaventa, `c10/s10` pasa de separador técnico a tarjeta de Gestión de
  la capacidad, con resumen y detalle por filesystem. Acción Fiduciaria no
  declara la fuente, por lo que conserva el separador y su bolsa manual.
- El detalle incorpora una gráfica horizontal de ocupación por filesystem,
  con escala explícita de 0 a 100 %. No asigna semáforos ni umbrales que la
  fuente no declare.
- El centro de carga de Novaventa identifica la plantilla mensual como
  consolidado y `Data_<mes>.xlsx` como fuente alternativa de alertas. Así el
  archivo Data no puede confundirse con el insumo que aporta `Capacidad`.
- El lector de `Data_<mes>` toma únicamente el bloque continuo de alertas y
  excluye la tabla dinámica de resumen que algunos archivos anexan al final;
  esta no contiene IDs ni fechas de casos. La cabecera de `Capacidad` se
  resuelve por su fila declarada antes de leer las columnas de periodo.
- Si `Data_<mes>` trae filas de otro corte, no reemplaza la cifra certificada
  por la hoja `Casos`: deja visible ese respaldo, registra la advertencia y
  pide el Data del periodo. Solo bloquea cuando no existe una cifra
  certificada que pueda conservar.
- Novaventa declara `Disponibilidad Real` en `Grafica Dispo y Gestion` como
  su matriz de corte vigente. La primera hoja homónima termina en jun-25;
  esta tabla contiene la disponibilidad real de jun-26 y sus CIs.
- La taxonomía de indicadores también se declara por perfil: para Novaventa,
  `Cumplimiento tiempos de Atención` es Gestión del Servicio. No se fuerza el
  nombre de Acción Fiduciaria (`tiempos de solución`) sobre otro cliente.
- La línea base y el preset inicial también son propios: Administración remota
  de Bases de datos, 48 BD SQL Server, 7 BD DB2 y vigencia del 21/07/2025 al
  20/07/2026. El preset incorpora capacidad y el anexo Db2; excluye bolsa de
  horas, mitigaciones y el duplicado de disponibilidad por CI, sin evidencia
  de que formen parte del informe de referencia de Novaventa.
- Las specs de perfil e inventario documentan el límite y las pruebas estáticas
  cubren la declaración, el dominio separado y la activación exclusiva.
- El HTML incorpora un control compacto de **Cliente activo** que abre el
  administrador. Desde allí se pueden crear, editar y eliminar perfiles personalizados. Cada
  ficha guarda identidad, contrato y su preset de tarjetas en el navegador, y
  se crea a partir de una plantilla de validación base (Acción Fiduciaria o
  Novaventa). El alta solo solicita el dato contractual que no llega en los
  insumos mensuales; las métricas y resultados se interpretan al cargarlos.
  Esa plantilla, no una regla escrita libremente, define los insumos y las
  validaciones disponibles para el cliente.
- El administrador separa visualmente la lista de perfiles del alta guiada y
  reduce las explicaciones permanentes mediante un detalle desplegable. El
  selector de insumos actualiza esa explicación sin repintar el formulario,
  por lo que no pierde nombre, fechas ni foco. El control de la barra anuncia
  el estado abierto del diálogo y recupera el foco al cerrarlo.
- Al cambiar tarjetas desde el botón **Tarjetas** en un perfil personalizado,
  la selección se actualiza también dentro de su ficha persistida. Los
  perfiles base están protegidos: se pueden seleccionar, pero no borrar.

La inspección de `Novaventa/Plantilla_  Novaventa Mayo.xlsx` confirmó para
junio de 2026 `/db2dta1 = 56,5 %` y `/db2dta2 = 49 %`; la fuente se trata como
ocupación de filesystems, no como horas contratadas o consumidas. La vista
redondea a `57 %` y `49 %`, igual que la diapositiva 10 de la referencia.

## Verificación realizada

- `python3 -m unittest discover -s automatizacion -p 'test_*.py'` — 71 pruebas
  correctas.
- `python3 automatizacion/verificar_ab.py --autoprueba` — el arnés distinguió
  los fixtures idénticos de dos regresiones introducidas a propósito.
- Validación sintáctica de los nueve bloques JavaScript propios del HTML —
  sintaxis correcta.
- `git diff --check` — sin errores de espacio.
- Inspección del Excel real con `openpyxl` — hoja `Capacidad`, encabezado en
  fila 4 y dos filesystems de Novaventa para junio de 2026 confirmados.
- Revisión de cobertura de los insumos reales: el consolidado disponible
  aporta los tres indicadores de junio, disponibilidad real y SETI de junio
  (100 % en DB2 y SQL Server), backups, Casos (6 alertas, 0 requerimientos y
  5 incidentes) y Capacidad (`/db2dta1 = 56,5 %`, `/db2dta2 = 49 %`).
  `Data_Mayo 2026.xlsx` contiene 20 alertas fechadas exclusivamente en
  febrero de 2026; no sustituye la cifra de junio certificada en `Casos`.
  El export GLPI de Novaventa sí tiene filas de junio y julio.
- Ante un Data válido pero fuera del corte, el lector conserva el respaldo de
  `Casos` cuando existe, muestra la advertencia y nunca lo presenta como una
  ausencia confirmada ni borra la serie del consolidado.

La interfaz de clientes se verificó visualmente en navegador local mediante un
servidor temporal, porque el navegador integrado no navega a `file://`. Se
revisaron escritorio y 720 × 900 sin desbordamiento ni errores en consola; el
cambio de plantilla conservó nombre y fechas, el detalle progresivo respondió
y Escape devolvió el foco al control superior. El entregable sigue siendo un
único HTML compatible con `file://`; el servidor se usó solo para la prueba.

## Archivos tocados

- `perfiles/novaventa.js`
- `informe-accion-fiduciaria 1.html`
- `automatizacion/test_specs_perfil_cliente.py`
- `automatizacion/test_specs_inventario_tarjetas.py`
- `openspec/changes/2026-08-05-f6-perfil-novaventa/`
- `openspec/specs/perfil-cliente/spec.md`
- `openspec/specs/inventario-tarjetas/spec.md`
- `docs/2026-08-04-plan-multicliente.md`
- `docs/2026-08-05-registro-persistente-clientes.md`

## Pendiente

- Cargar el consolidado de Novaventa en una sesión visual que admita `file://`
  y cotejar la tarjeta contra la diapositiva 10 del informe de junio.
- Generar los dos exportes reales de Acción Fiduciaria, ejecutar la comparación
  A/B contra `main` y completar la publicación remota de F6.
- Obtener el `Data_<mes>`/AlertsList de junio que permita conciliar contra
  los 6 casos certificados por el consolidado. La matriz de disponibilidad
  del corte ya está identificada y declarada en `Grafica Dispo y Gestion`.
- **Regla de plataforma vigente:** el usuario puede seleccionar clientes,
  registrar perfiles guiados y persistir su preset. Para que un cliente tenga
  validaciones propias distintas de AF o Novaventa, primero se debe incorporar
  y probar una nueva plantilla de validación declarativa; no se habilitan
  mapeos de Excel arbitrarios desde la interfaz.
