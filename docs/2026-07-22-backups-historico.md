# Matriz histórica de backups

## Objetivo

Representar en un único plano todas las ejecuciones mensuales de cada instancia, desde el inicio del contrato hasta el período reportado. La matriz reemplaza la lista del último corte dentro del modal; la diapositiva heredada permanece como soporte compatible del informe.

## Fuente y alcance temporal

- Fuente: hoja `Backups` del consolidado de disponibilidad.
- Filas: valores reales de la columna `INSTANCIAS`.
- Columnas: todas las fechas reconocibles de la hoja.
- Inicio: primer mes igual o posterior a la fecha contractual `data-k="finicio"`.
- Fin: mes y año seleccionados como período del informe.
- Las columnas anteriores al contrato y posteriores al corte se excluyen.

Para el consolidado verificado el 22 de julio de 2026, la hoja contiene 14 instancias y 19 meses entre diciembre de 2024 y junio de 2026. Con contrato iniciado el 1 de septiembre de 2025 y corte junio de 2026, la matriz publica diez meses: septiembre de 2025 a junio de 2026.

## Modelo del store

```js
REPORTE.d('backups').datos = {
  instancias: [{ nombre, valor }],
  promedio,
  completas,
  etiqueta,
  historico: {
    periodos: [{ clave, etiqueta, mes, anio }],
    instancias: [{ nombre, valores: [100, 100, null, 0, 85] }]
  }
};
```

Los arreglos `valores` están alineados uno a uno con `periodos`.

## Estados visuales

| Condición | Estado | Color | Marca visible |
| --- | --- | --- | --- |
| `valor >= 99.99` | Ejecución completa | Verde | `✓` |
| `0 < valor < 99.99` | Ejecución parcial | Naranja | Porcentaje redondeado |
| `valor === 0` | No ejecutada | Rojo | `×` |
| Vacío, texto no numérico o `N/A` | Sin dato | Gris | `—` |

El color nunca es el único medio de interpretación. Cada celda también contiene una marca y un nombre accesible con instancia, mes, porcentaje exacto y estado.

## Filtros

La matriz reutiliza el estándar histórico del informe:

- Presets `3M`, `6M`, `12M` y `Todo`.
- Selectores `Desde` y `Hasta` restringidos al rango contractual cargado.
- El valor inicial es `Todo`, por lo que el modal abre mostrando el contrato completo hasta el corte.
- El rango seleccionado se conserva mientras el informe permanezca abierto.

## Interacción

- Seleccionar una celda muestra debajo la instancia, el mes, el porcentaje exacto y el estado.
- Sin selección, la franja inferior resume las verificaciones completas, parciales, no ejecutadas y sin dato del rango visible.
- Los filtros actualizan únicamente la matriz para evitar reconstruir el modal o perder el foco.

## Validaciones

- Una celda vacía no se convierte en cero.
- El mes del informe debe existir en la hoja; de lo contrario, el dominio se marca inválido.
- El promedio del corte ignora las celdas sin dato.
- Las instancias del corte y la última columna del histórico provienen de la misma celda del Excel.
- Las autopruebas cotejan el número de instancias, los valores del corte y los extremos contractuales del histórico.

## Exportación

La matriz forma parte del dominio `backups` incluido en `snapshotEstado()`. El HTML entregable conserva filtros y selección; durante el PDF los controles se ocultan y permanece la matriz con el rango activo.
