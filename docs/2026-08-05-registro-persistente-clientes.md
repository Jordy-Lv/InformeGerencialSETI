# Registro persistente de clientes, presets y validaciones

## Contexto

El informe dejó de ser una pantalla fija para Acción Fiduciaria y Novaventa:
la persona que prepara un informe debe poder seleccionar un cliente, conservar
su composición de tarjetas y administrar sus perfiles sin duplicar el HTML ni
crear automatizaciones por cliente. La capacidad sigue funcionando sin
servidor, al abrir un único archivo mediante `file://`.

Esta guía documenta el comportamiento entregado en F6 y establece el límite
del registro guiado: un cliente personalizado reutiliza una plantilla de
validación que ya fue comprobada. No se admiten lectores de Excel, reglas de
clasificación o mapeos libres escritos desde la interfaz.

## Qué se implementó

### Perfiles base y perfiles personalizados

- **Acción Fiduciaria** y **Novaventa** son perfiles base protegidos. Sus
  objetos siguen viviendo como datos puros en `perfiles/`.
- El control **Cliente activo** abre el administrador de perfiles. Permite
  cambiar, crear, editar y eliminar únicamente clientes personalizados.
- El control identifica visualmente el cliente seleccionado y comunica si el
  diálogo está abierto. Al cerrarlo, el foco regresa al punto de entrada para
  que el flujo también funcione con teclado.
- Los seis controles de la barra superior comparten una escala compacta de
  140 × 40 px en escritorio. Se retiró la nota sobre **Editar datos** porque
  repetía una acción que el propio botón ya comunica.
- La creación solicita nombre, el tipo de insumos y la fecha de inicio
  contractual. La fecha se obtiene del contrato o acta de inicio, pues no es
  un dato que llegue normalmente en los insumos mensuales. El identificador
  estable se genera a partir del nombre y no puede colisionar con otro cliente.
- La configuración se guarda en el navegador bajo
  `informe:clientes:registro:v1`. Es persistencia local del equipo y del
  navegador actual; no sincroniza datos entre computadores ni navegadores.

### Plantilla de validación

- Todo cliente personalizado debe escoger una plantilla: por ahora **Acción
  Fiduciaria** o **Novaventa**.
- La plantilla es quien declara los insumos aceptados, sus hojas, columnas,
  estrategias de lectura y criterios de carga. Por ejemplo, un cliente que
  use Novaventa conserva la interpretación de `Data_<mes>` y `Capacidad`;
  uno que use Acción Fiduciaria conserva sus reglas vigentes.
- El alta no repite alcance, instancias, metas, indicadores ni una matriz de
  tarjetas: todos esos resultados deben leerse de los insumos. El preset se
  ajusta después con el botón **Tarjetas**, que ya limita la selección a lo
  compatible con el perfil.
- La relación completa de datos esperados se muestra bajo **La automatización
  interpreta al cargar** como un detalle desplegable. Así permanece disponible
  sin ocupar el espacio principal del formulario.
- Cambiar el tipo de insumos actualiza únicamente ese detalle. El formulario
  no se vuelve a construir y conserva nombre, fechas y foco.
- El administrador es una herramienta de autoría. Aunque se haya abierto antes
  de exportar, el diálogo y la barra superior se eliminan del HTML que recibe
  el cliente.
- Una validación verdaderamente distinta requiere una nueva plantilla de
  perfil y su evidencia real, especificación OpenSpec y pruebas. Bancóldex
  es el siguiente caso de este tipo; no debe crearse como una copia de
  Novaventa o AF.

### Preset de tarjetas

- El botón **Tarjetas** sigue permitiendo ajustar la vista del informe.
- Para un perfil personalizado, al aplicar el preset se guarda tanto el
  override de la sesión como la selección en la ficha persistente del cliente.
  Al volver a abrir el HTML y seleccionar ese cliente, se recupera la misma
  composición.
- Los criterios de carga se derivan de las tarjetas activas; retirar una
  tarjeta deja de exigir únicamente sus criterios declarados.
- Los presets y otros datos operativos usan claves por id de cliente, por lo
  que una selección no contamina la bolsa manual ni las posiciones de Acción
  Fiduciaria.

### Eliminación

- Los perfiles base no se eliminan desde la interfaz.
- Al eliminar un cliente personalizado se borra su ficha y su preset local.
- Si el cliente eliminado está activo, el informe vuelve a la plantilla de
  la que heredaba. No modifica dicha plantilla ni otro cliente.

## Uso operativo

1. Abra el HTML actualizado y pulse el control del **Cliente activo** en la
   barra superior.
2. Para crear uno, complete el nombre, el tipo de insumos y la fecha de
   inicio que figure en el contrato o acta.
3. Si necesita confirmar lo que leerá la plantilla, despliegue **La
   automatización interpreta al cargar** sin salir del formulario.
4. Cargue los insumos que la plantilla solicita; el centro de carga muestra
   sus validaciones y bloquea exportaciones cuando falte una fuente obligatoria.
5. Use **Tarjetas** si necesita afinar el preset para ese cliente. La elección
   queda registrada en su ficha.
6. Para retirar un cliente creado por error u obsoleto, use **Eliminar** en
   el administrador. La confirmación no afecta perfiles base.

## Verificación realizada

- `python3 -m unittest discover -s automatizacion -p 'test_*.py'` — **71
  pruebas correctas**. Incluye las comprobaciones del registro local,
  plantilla, conservación del formulario, poda del diálogo en el export,
  preset persistente y protección de perfiles base.
- Validación sintáctica de los nueve bloques JavaScript propios del HTML —
  **sintaxis correcta**.
- `git diff --check` — **sin errores de espacio**.
- Se verificó estáticamente que un perfil personalizado se resuelve desde el
  registro local o desde un HTML exportado, conservando su perfil embebido
  para que el entregable no dependa de la configuración local de quien lo
  generó.
- La prueba visual en navegador cubrió escritorio y una ventana de 720 × 900:
  no hubo desbordamiento horizontal ni errores en consola. Se verificó el
  detalle desplegable, el cambio de plantilla sin pérdida de nombre o fechas,
  y el cierre con Escape con devolución de foco y `aria-expanded=false`.

La comparación A/B real de Acción Fiduciaria contra `main` continúa como cierre
global de F6. Esta mejora de autoría no modifica el informe del cliente: la
barra y el diálogo se podan explícitamente antes de serializar el export.

## Archivos tocados

- `informe-accion-fiduciaria 1.html`
- `automatizacion/test_specs_perfil_cliente.py`
- `openspec/changes/2026-08-05-f6-perfil-novaventa/{proposal.md,design.md,tasks.md}`
- `openspec/changes/2026-08-05-f6-perfil-novaventa/specs/perfil-cliente/spec.md`
- `openspec/specs/perfil-cliente/spec.md`
- `docs/2026-08-05-f6-perfil-novaventa.md`
- `docs/2026-08-04-plan-multicliente.md`

## Pendiente

- Crear y verificar la plantilla de validación de Bancóldex a partir de sus
  insumos reales; no reutilizar una plantilla incompatible.
- Ejecutar la comparación A/B de Acción Fiduciaria con exportaciones reales
  antes de cerrar F6.
- Completar la prueba visual de carga y exportación con los insumos reales de
  Acción Fiduciaria como parte de la comparación A/B de F6.
- Mantener esta documentación, el documento de sesión F6, la spec vigente y
  sus pruebas actualizados en el mismo cambio cuando se agregue una capacidad
  o se modifique una validación.
