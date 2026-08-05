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

La fuente `Data_<mes>` se declara después de AlertOps. Cuando AlertOps no trae
filas del periodo, el consolidado la cubre; las discrepancias se conservan en
la reconciliación interna.
