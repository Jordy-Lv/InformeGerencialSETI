# Automatización de la sábana de casos (GLPI)

Origen: encargo de Santiago Amaya Cely en la llamada del 23/07/2026 —
*«mira cómo puedes automatizar esa parte con el GLPI… puede que haya otra forma»*.
Diagnóstico completo en [`../docs/2026-07-23-automatizacion-glpi-diagnostico.md`](../docs/2026-07-23-automatizacion-glpi-diagnostico.md).

## Qué hay aquí hoy

| Archivo | Qué es |
|---|---|
| `sonda_glpi.py` | Reconocimiento. Averigua **qué vía de extracción funciona** contra la instancia real y guarda la evidencia. No es todavía el extractor mensual. |
| `.env.ejemplo` | Plantilla de credenciales. Cópiala a `.env` (ignorado por git). |

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
