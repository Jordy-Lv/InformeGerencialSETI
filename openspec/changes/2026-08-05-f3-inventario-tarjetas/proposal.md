# F3 — Inventario declarativo de tarjetas

## Contexto

Las diez tarjetas de Acción Fiduciaria ya existen en el DOM, pero sus dominios, fuentes, validaciones y renderizadores están repetidos en listas manuales.

## Propuesta

Introducir un inventario declarativo y declarar en el perfil cuáles tarjetas componen el informe. Durante F3 el HTML sigue siendo la vista existente: el inventario deriva dominios, extensiones admitidas, criterios de carga y orden de renderizado, y comprueba su correspondencia con el DOM. La generación de HTML y la selección editable quedan para F4.

## Fuera de alcance

- Cambiar cifras, textos, aspecto o páginas visibles de Acción Fiduciaria.
- Generar tarjetas desde una plantilla o persistir presets (F4).
- Crear perfiles o adaptadores para otros clientes.
