# Tarjetas faltantes del informe de Bancoldex

## Contexto

El entregable histórico de Bancoldex es
`Bancoldex/reporte-bancoldex-2026-07-02.pdf` (11 páginas, junio de 2026).
El informe web ya cubre 7 de sus 11 páginas con el preset actual
(`c3, c4, c5, c7, c8, c8m`). Se auditó página por página contra el motor y
quedan tres huecos, decididos con el usuario el 07/08/2026.

| Página del PDF | Estado hoy | Decisión |
|---|---|---|
| 2. Línea base del servicio | `c3` sin la tabla base/actual | Tarjeta nueva |
| 3. Control línea base | Sin cubrir | Misma tarjeta nueva, en el modal |
| 4. Indicadores | `c4` con 3 de 4 métricas | **Fuera de alcance** (ver abajo) |
| 9. Acciones y mejoras | `c8m` pinta 2 de 6 columnas | Completar |
| 11. Firmas aprobadoras | Sin cubrir | Tarjeta nueva |

## Qué se propone

1. **`c13` — Control de línea base.** Tarjeta nueva: resumen por categoría
   (base contrato / actual / diferencia) en la tarjeta colapsada, y el
   detalle por tipo de infraestructura en el modal. Mismo patrón de
   tarjeta + modal que ya usan `c5` y `c7`.

2. **`c14` — Firmas aprobadoras.** Tarjeta nueva con los tres firmantes.
   Cada uno firma **en el propio informe**, trazando sobre un `<canvas>`
   con puntero o dedo. El trazo se guarda como PNG en el almacén del
   cliente y se reutiliza en los periodos siguientes; en el export sale
   como imagen embebida en base64.

3. **`c8m` — Acciones y mejoras completa.** El libro mensual de Bancoldex
   ya trae `RESPONSABLE`, `FECHA ENTREGA`, `OBSERVACIONES` y `ESTADO`
   (fracción de avance). El renderizador los lee y los descarta. Se
   pintan, con el anillo de avance que el PDF muestra como dona.

## Fuera de alcance, explícitamente

- **`c4` (Indicadores) no se toca.** El PDF muestra 4 filas —incluida
  `Ejecución de Backups`— y doble columna `BANCOLDEX`/`SETI` por mes, y la
  hoja `Indicador` del consolidado tiene ambas cosas. **Decisión del
  usuario (07/08/2026): Gestión de backups conserva su tarjeta
  independiente (`c7`) tal como está hoy**, y no se convierte en una fila
  del cuadro de indicadores. La doble columna `BANCOLDEX`/`SETI` queda
  registrada como hallazgo, no como trabajo: hoy el motor lee solo la
  columna del cliente y hay meses donde las dos difieren (100 % / 99,7 % y
  99,34 % / 100 % en Disponibilidad).
- **`c12` (Anexos) y `c9` (bolsa de horas / TYA) siguen apagadas** para
  Bancoldex, por decisión del usuario.
- **No se copian las gráficas del PDF.** El usuario lo pidió explícitamente:
  esto es sobre qué tarjetas faltan, no sobre replicar su estética.

## Por qué las cifras de `c13` se declaran en el perfil

La hoja `Linea Base` del consolidado real trae `CI · MOTOR · AMBIENTE ·
CANTIDAD(base) · CANTIDAD(actual)`, 13 filas, y suma **220 / 161**. El PDF
aprobado dice **237 / 257**. No cuadran, y no existe en el repositorio la
fuente que produce las cifras del PDF.

Decisión del usuario: las cifras se **declaran en `perfiles/bancoldex.js`**,
reproduciendo el entregable aprobado. Es coherente con lo que ya hace el
perfil (`lineaBase.estadisticas` ya trae `257` escrito a mano) y con el
principio rector: son números que un algoritmo existente sabe pintar, no una
decisión de cómo se recorre una estructura. Leerlas del consolidado queda
como trabajo posterior, cuando se sepa de dónde sale el 237/257.

## Riesgo principal

`c8m` y el HTML son compartidos con **Acción Fiduciaria, que está en
producción**. Se comprobó que su libro usa otro formato: una sola hoja con
`Cliente · Descripción · Dato / evidencia` y secciones separadas por
filas-título, sin responsable, fecha, observaciones ni estado. Enriquecer
`c8m` globalmente dejaría cuatro columnas vacías en el informe de AF y
rompería la restricción inviolable #2. Por eso las columnas nuevas se
declaran por perfil y AF, que no declara ninguna, debe renderizar
exactamente igual que hoy — verificado con A/B en cero.
