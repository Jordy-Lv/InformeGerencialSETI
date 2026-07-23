# Automatización de la sábana de casos (GLPI)

Origen: encargo de Santiago Amaya Cely en la llamada del 23/07/2026 —
*«mira cómo puedes automatizar esa parte con el GLPI… puede que haya otra forma»*.
Diagnóstico completo en [`../docs/2026-07-23-automatizacion-glpi-diagnostico.md`](../docs/2026-07-23-automatizacion-glpi-diagnostico.md).

## Qué hay aquí hoy

| Archivo | Qué es |
|---|---|
| `sonda_glpi.py` | Reconocimiento. Averigua **qué vía de extracción funciona** contra la instancia real y guarda la evidencia. |
| `extraer_glpi.py` | Extrae la sábana por la API REST y genera el CSV y el `insumos-af.js` que lee el informe. |
| `.env.ejemplo` | Plantilla de credenciales. Cópiala a `.env` (ignorado por git). |

## Cómo se conecta con el informe

```
extraer_glpi.py  →  salida/glpi-2026-06.csv      la sábana, para archivo y auditoría
                 →  salida/insumos-af.js         lo que lee el informe
```

`insumos-af.js` se copia **junto al HTML**. Al abrirlo, el informe lo detecta y
carga los casos sin que nadie arrastre nada. Si el archivo no está, el centro de
carga funciona igual que siempre: **la carga manual nunca dejó de existir.**

No puede ser un `.json` leído con `fetch`: abierto desde el disco, el navegador
bloquea toda petición al sistema de archivos. Un `<script>` vecino sí carga, y
es la única puerta que queda sin montar un servidor.

Ese archivo se carga sin que nadie lo apruebe, así que el informe lo trata como
origen no confiable: comprueba formato, periodo declarado y **huella SHA-256**
del contenido antes de aceptarlo. Si algo no cuadra, avisa y no carga nada.

Verificado en el navegador: la carga automática deja los 8 casos de mayo de 2026
con su trazabilidad completa y ajusta el periodo del informe al del insumo; un
contenido alterado se rechaza por la huella y el informe queda en manual.

**Pendiente de comprobar en el equipo donde se use:** si el navegador cachea
`insumos-af.js` entre aperturas. El informe le añade un sufijo variable para
evitarlo, pero en el visor de pruebas siguió sirviéndose de caché. Como defensa
de fondo, el aviso de carga **siempre muestra la fecha de extracción**: si
apareciera un insumo viejo, la fecha lo delata.

## Cómo ejecutar la sonda

```bash
cp automatizacion/.env.ejemplo automatizacion/.env
# completar GLPI_USER y GLPI_PASSWORD en ese archivo, y luego:
python3 automatizacion/sonda_glpi.py
```

La sonda lee `.env` por su cuenta — no hace falta `source`, que además obliga a
entrecomillar cualquier valor con espacios. Si prefieres variables de entorno
(por ejemplo en el servidor), tienen prioridad sobre el archivo.

Solo necesita Python 3, sin dependencias externas: así puede correr tal cual en
el servidor donde acabe viviendo la tarea programada.

Deja la evidencia en `automatizacion/salida/` — HTML de cada respuesta y el CSV
si logró exportarlo. **Esa carpeta está en `.gitignore`**: las respuestas crudas
traen casos de todos los clientes de SETI, no solo de Acción Fiduciaria.

## Qué prueba, y en qué orden

1. **API REST** (`/apirest.php/initSession`) — la vía limpia. Si responde, se
   construye sobre ella y no hace falta nada más.
2. **Sesión web** — login por formulario con el token `_glpi_csrf_token`, igual
   que lo haría un navegador, pero sin navegador.
3. **searchOptions** — descubre qué número identifica a «Entidad» y a «Fecha de
   apertura» *en esta instalación*. Los IDs cambian entre versiones y plugins;
   por eso se descubren en vez de escribirse a mano.
4. **Exportación CSV** — `display_type=3` con `export_all=1` (todas las páginas,
   no solo la visible). Prueba dos veces: sin filtrar, y filtrando por entidad
   dentro de GLPI.

## Credenciales

- **Cuenta de servicio de solo lectura**, no la personal de nadie.
- Nunca dentro de este repositorio, del HTML ni de un archivo versionado.
- En el servidor definitivo: gestor de secretos del sistema o Key Vault.

## Lo que falta

- Ejecutar la sonda y decidir la vía con el resultado en la mano.
- Extractor mensual + depósito en SharePoint/OneDrive.
- Generación de `insumos-af.js` y el arranque que lo consume en el informe.
- Programación, alerta ante fallo y responsable operativo.
