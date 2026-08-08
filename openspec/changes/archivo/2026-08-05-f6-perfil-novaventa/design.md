# Diseño — F6 perfil Novaventa

El perfil `novaventa` extiende `accion-fiduciaria`; la resolución conserva la
fusión profunda existente y el arreglo de tarjetas se declara de forma
explícita. El perfil solo sobrescribe identidad, textos, metas, filtro GLPI,
fuentes de alertas y consolidado, y la composición que añade capacidad.

La estrategia `bloque-con-fechas` identifica filas candidatas por los campos
requeridos y escoge únicamente la que también tiene columnas de fecha. Si cero
o más de un bloque contienen fechas, el dominio queda inválido con las filas
candidatas. Así el bloque de metas de las filas 2–5 no puede usarse como serie
histórica.

La fuente `Data_<mes>` se declara después de AlertOps. Si ese Data pertenece a
otro corte, no reemplaza la cifra certificada de `Casos`; se conserva el
respaldo y queda una advertencia explícita. Sin respaldo, el corte se bloquea.
Las discrepancias se conservan en la reconciliación interna.

Novaventa declara `Grafica Dispo y Gestion` / `Disponibilidad Real` como
fuente de disponibilidad del corte. La estrategia `tabla-con-fechas` encuentra
el rótulo de la tabla, sus columnas de fecha y los motores/CI de las filas
continuas. Así no confunde la matriz histórica de la hoja `Disponibilidad`,
que termina en jun-25, con la disponibilidad de jun-26.

La misma fuente de configuración declara los alias de las tres métricas. En
particular, «Cumplimiento tiempos de Atención» corresponde a Gestión del
Servicio para Novaventa; el lector no presupone el literal de Acción
Fiduciaria («tiempos de solución»).

La ocupación de filesystems de la hoja `Capacidad` no representa una bolsa de
horas. Se publica bajo el dominio independiente `capacidad` y se expone en la
tarjeta `c10`, que Novaventa añade a su selección. La tarjeta `c9` y el
dominio `bolsa` no reciben datos ni cambios de persistencia; Acción Fiduciaria
no declara capacidad y conserva su separador de Informe técnico.

## Registro local de clientes

Los perfiles base (`accion-fiduciaria` y `novaventa`) siguen siendo archivos
de datos puros. Los clientes creados por el usuario se almacenan bajo una sola
clave local versionada (`informe:clientes:registro:v1`) y contienen únicamente
datos serializables: identidad, contrato, plantilla y selección de tarjetas.
No se guarda ni evalúa código del usuario.

Un cliente personalizado extiende una plantilla base elegida de forma
explícita. La plantilla aporta las fuentes, mapeos y validaciones de insumos.
El alta solo solicita identidad y la fecha de inicio contractual, ya que este
dato no llega normalmente en los insumos mensuales. Indicadores, metas,
disponibilidad, capacidad, backups e inventario se interpretan al cargar los
archivos; no se copian de la plantilla como datos del nuevo cliente. El
selector visual abre un único administrador, donde también se cambia el
cliente activo, evitando un selector nativo redundante en la barra superior.

Cuando se aplica el selector habitual de tarjetas en un cliente personalizado,
la misma selección se actualiza además dentro de su registro persistente. La
personalización se hace después de crear el cliente para no convertir el alta
en una matriz de casillas. Los perfiles base no se editan ni se eliminan. Al
borrar un cliente personalizado, se borra solo su ficha y su preset local; si
estaba activo, se vuelve a la plantilla desde la que heredaba.

El administrador usa una sola superficie compacta: a la izquierda reúne el
cambio de perfil y las acciones de cada cliente; a la derecha organiza el alta
en identidad e insumos, vigencia contractual y el paso posterior de Tarjetas.
La lista extensa de datos que interpreta cada plantilla queda en un detalle
desplegable. Cambiar el tipo de insumos actualiza únicamente ese detalle: no
reconstruye el formulario, por lo que conserva nombre, fechas y foco. El
control de la barra mantiene `aria-expanded`, el diálogo conserva el foco
contenido y al cerrar lo devuelve al control que lo abrió.

Como el diálogo se crea bajo demanda en `body`, `podarClon()` lo elimina de
forma explícita junto con la barra superior. Haber abierto el administrador
durante la autoría no incorpora esa interfaz en el HTML entregado al cliente.

La barra superior usa una retícula compacta común para sus seis controles:
140 × 40 px en escritorio, con el mismo radio y reducción uniforme en anchos
intermedios. Se elimina la ayuda «Haz clic en Editar datos» porque duplica el
nombre y la función del botón; el estado activo continúa comunicándose en el
propio control mediante texto, icono y estilo.
