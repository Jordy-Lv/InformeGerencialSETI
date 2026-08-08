# F1 — Perfil de cliente y export autocontenido

## Contexto

El informe de Acción Fiduciaria tenía datos del cliente repetidos dentro del
motor. La primera parte de F1 los extrae a un perfil de datos y prepara claves
de almacenamiento por perfil sin modificar el resultado visible.

Durante la autoría el perfil se carga desde `perfiles/accion-fiduciaria.js`.
El entregable, en cambio, debe seguir siendo un único HTML: no puede conservar
esa dependencia cuando se exporta.

## Propuesta

- Registrar y resolver perfiles de datos puros por identificador.
- Usar el perfil de Acción Fiduciaria en los filtros y el store ya migrados en
  este incremento.
- Incluir el perfil resuelto en `window.__ESTADO__` y retirar del clon exportado
  el script vecino usado durante la autoría.
- Hidratar desde `PERFIL.textos` los textos de presentación, mensajes y
  metadatos de exportación que antes repetían el nombre del cliente.
- Conservar la lectura de las claves históricas de posiciones y bolsa.
- Fijar estas invariantes con autopruebas embebidas y pruebas estáticas en
  biblioteca estándar.

## Fuera de alcance

- Agregar un segundo cliente o herencia entre perfiles reales.
- Cambiar cifras, textos o comportamiento visible de Acción Fiduciaria.
- Crear el dorado de F0 para junio de 2026; la evidencia real disponible para
  este change corresponde a julio de 2026.
