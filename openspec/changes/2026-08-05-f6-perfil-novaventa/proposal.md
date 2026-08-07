# F6 — Perfil Novaventa

## Contexto

Novaventa comparte GLPI, taxonomía y varias hojas de consolidado con Acción
Fiduciaria. Sus insumos reales añaden dos diferencias verificadas: `Data_<mes>`
es una fuente alternativa de alertas y la hoja Indicadores contiene un bloque
de metas sin fechas antes del bloque histórico.

## Propuesta

Añadir el perfil Novaventa como herencia de Acción Fiduciaria, resolverlo de
forma explícita en el informe y declarar sus fuentes y metadatos como datos.
Incorporar la estrategia `bloque-con-fechas` para escoger el bloque histórico
de indicadores, declarar `Disponibilidad Real` como la tabla de corte vigente
cuando la matriz homónima solo conserva histórico, y una tarjeta de capacidad
alimentada desde su hoja Capacidad.

Como alcance solicitado durante F6, convertir los perfiles demostrados en una
capacidad de plataforma local: el usuario puede seleccionar un cliente,
registrar o editar un perfil personalizado a partir de una plantilla de
validación existente y conservar su configuración en el navegador. El alta
no duplica métricas que los insumos ya contienen; la composición de tarjetas
se ajusta después desde su selector especializado. Los perfiles base se
mantienen protegidos. Refinar el administrador como una superficie compacta y
accesible, con detalle progresivo de los insumos y sin reconstruir ni borrar
campos cuando el usuario cambia de plantilla.

## Fuera de alcance

- Modificar cifras o comportamiento de Acción Fiduciaria.
- Implementar todavía una plantilla de validación propia para Bancoldex.
- Convertir la bolsa manual de AF en una regla de capacidad.
- Permitir lectores, hojas o reglas arbitrarias sin declararlas y validarlas
  previamente en una plantilla de perfil.
