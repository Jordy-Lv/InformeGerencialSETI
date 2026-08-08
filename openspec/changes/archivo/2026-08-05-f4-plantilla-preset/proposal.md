# F4 — Plantilla de tarjetas y preset persistido

## Contexto

F3 ya convirtió el inventario de Acción Fiduciaria en la fuente de verdad de
dominios, fuentes, criterios y renderizadores, y se cerró con un A/B real de
`0 diferencias`. Aún quedan diez envolturas de tarjeta escritas a mano en el
panel y el perfil no puede elegir una composición temporal sin editar código.

## Propuesta

Hacer que la interfaz de tarjetas se construya desde los descriptores ya
resueltos, manteniendo las diapositivas legado como destino de los parsers y
de la captura PDF. Añadir un selector accesible que permita aplicar un preset
local por perfil, informar los criterios que cambian y persistir solamente
esa elección en el navegador. El exportado llevará la selección efectiva.

## Fuera de alcance

- Alterar cifras, textos o el preset predeterminado de Acción Fiduciaria.
- Crear tipos nuevos de tarjeta, componentes o perfiles de otros clientes.
- Reemplazar los nodos de diapositiva que hoy escriben los parsers.
- Convertir el informe en una aplicación que requiera servidor o build.
