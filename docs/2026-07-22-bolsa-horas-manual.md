# Bolsa de horas editable

## Objetivo

Transformar el contenido de la diapositiva de PowerPoint en un indicador vivo del informe. La tarjeta, el modal, el HTML exportado y el PDF consumen el mismo dominio `REPORTE.bolsa`.

## Datos editables

- Horas contratadas.
- Horas consumidas durante el mes reportado.
- Saldo disponible, con cálculo automático y corrección manual permitida.
- Observación adicional opcional.

Al cambiar el consumo o la capacidad, el saldo disponible se recalcula automáticamente. La tercera casilla permanece editable para permitir una corrección explícita cuando el saldo confirmado provenga de otra fuente. La fecha de corte no se solicita al usuario: se calcula como el último día del mes seleccionado en el informe.

## Modelo publicado

```js
REPORTE.publicar('bolsa', {
  estado: 'valido',
  datos: {
    fechaCorte: '2026-06-30',
    contratadas: 100,
    saldoInicialMes: 97,
    consumidasMes: 92,
    disponibles: 5,
    observacion: ''
  },
  fuente: REPORTE.procedencia('Registro manual de bolsa de horas')
});
```

`saldoInicialMes` representa las horas disponibles al comenzar el período. Normalmente `disponibles` es el resultado de restar el consumo mensual. Si el usuario modifica el saldo disponible, el sistema acepta esa corrección y reconstruye `saldoInicialMes` como `disponibles + consumidasMes`.

Para mantener compatibilidad con registros creados antes de este cambio, si falta `saldoInicialMes` se reconstruye como `disponibles + consumidasMes`. De esta forma no cambia el saldo final que ya estaba publicado.

## Cálculos

- Saldo disponible: `saldoInicialMes - consumidasMes`.
- Horas utilizadas antes del período: `contratadas - saldoInicialMes`.
- Horas utilizadas acumuladas: `contratadas - disponibles`.
- Disponibilidad de la bolsa: `disponibles / contratadas * 100`.

Ejemplo: si el mes comienza con 97 horas y se registran 92 consumidas, el sistema calcula 5 horas disponibles y una disponibilidad del 5 % sobre una bolsa de 100 horas.

## Validaciones

- La capacidad contratada debe ser mayor que cero.
- El saldo inicial y el consumo no pueden ser negativos.
- El saldo inicial no puede superar la capacidad contratada.
- El consumo mensual no puede superar el saldo inicial del mes.
- El saldo final debe ser exactamente `saldoInicialMes - consumidasMes`.
- El valor `0` es válido y no se interpreta como ausencia de información.

## Actualización y guardado automáticos

- Cada cambio válido actualiza inmediatamente las métricas, la barra morada, la escala y los textos del modal.
- Al editar consumo o capacidad, el saldo se descuenta automáticamente desde la base vigente.
- Al editar directamente el saldo disponible, ese valor se considera una corrección confirmada y pasa a ser la nueva referencia para cambios posteriores.
- El guardado en el dominio y en `localStorage` ocurre automáticamente después de una pausa breve de 220 ms.
- El formulario conserva el foco mientras se escribe; no repinta ni colapsa el editor en cada cambio.
- Si un valor es inválido, se muestra el motivo y ese borrador no reemplaza el último registro válido.
- No existe botón de guardar. El único control manual restante es **Borrar datos**.

## Persistencia y exportación

- La autoría guarda un registro por periodo en `localStorage` con la clave `informeAF:bolsa:AAAA-MM`.
- El dominio viaja en `snapshotEstado()` y se rehidrata en el HTML entregable.
- El formulario, los mensajes de autoría y sus controles se eliminan del HTML exportado.
- Durante la exportación PDF el formulario se oculta; la página utiliza únicamente el resumen final.

## Texto conservado

El modal genera automáticamente las frases heredadas del PPT con los valores registrados: cliente, consumo mensual, horas contratadas, saldo disponible, texto de seguimiento y cierre de atención.
