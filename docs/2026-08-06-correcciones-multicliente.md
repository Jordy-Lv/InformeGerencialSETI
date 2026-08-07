# Tres correcciones multicliente: preset, rótulos y almacén por cliente

**06/08/2026.** Change `2026-08-05-f6-perfil-novaventa`. Salen del
end-to-end de Bancoldex ([`2026-08-06-e2e-bancoldex.md`](2026-08-06-e2e-bancoldex.md))
y de una consulta del usuario sobre persistencia de insumos.

Las tres comparten causa: **solo se manifiestan en un cliente que no sea
Acción Fiduciaria.** AF selecciona las diez tarjetas, no declara meta de
backups y es el único con almacén propio desde siempre, así que cada defecto
era invisible desde el único cliente en producción.

---

## 1. El preset del perfil no se aplicaba en un equipo limpio

`tarjeta.hidden` lo pone únicamente `aplicarPresetTarjetas()`, y en el
arranque solo se llamaba si había un preset guardado:

```js
function restaurarPresetTarjetas(){
  const guardado=resolverPresetGuardado();
  if(guardado) aplicarPresetTarjetas(...);   // ← sin nada guardado, no hacía nada
}
```

Con `localStorage` vacío —la primera vez que alguien abre el archivo— el
preset declarado en `PERFIL.tarjetas.seleccionadas` nunca llegaba al DOM. En
Bancoldex quedaban visibles, y viajaban al HTML exportado:

| Tarjeta | Texto que salía en el informe de Bancoldex |
|---|---|
| c5 | «Requiere AlertsList y GLPI del periodo» (Bancoldex usa Aranda) |
| c6 / c11 | «Meta 99,30 %» — la meta de AF |
| c9 | «BOLSA DE HORAS» (Bancoldex no tiene bolsa) |
| c12 | «Informe_mensual_Oracle_**Accion_Fiduciaria**_Junio_2026» |

**Corrección:** aplicar siempre el preset, con el del perfil como base.

```js
aplicarPresetTarjetas((guardado||TARJETAS_SELECCIONADAS).map(t=>t.id),{persistir:false});
```

Un preset guardado sigue mandando sobre el del perfil. Para AF el efecto es
nulo: sigue mostrando las diez.

---

## 2. La tabla de indicadores conservaba los rótulos y metas de AF

`cargarIndicadores()` escribía solo las tres columnas de meses (`cells[j+2]`).
Las dos primeras celdas —nombre y meta— eran literales del HTML de AF que
nadie sobreescribía. La tarjeta resumen sí mostraba lo correcto, porque la
escribe `PERFIL.tarjetas.presentacion`; la tabla de detalle, no.

| Indicador | Bancoldex mostraba | Su Excel dice |
|---|---|---|
| Disponibilidad | 99,30 % | **99,98 %** |
| Gestión del Servicio | 95 % | **97 %** |
| Entregables | 90 % | **99 %** |

**Corrección:** escribir `cells[0]` con `rotuloIndicador()` y `cells[1]` con
la meta de la fuente. La meta se formatea con 2 decimales cuando no es entera
y con 0 cuando sí lo es. Una meta ilegible deja la celda como estaba, en vez
de vaciarla.

**Riesgo para AF, y por qué no se materializa.** Estas celdas son estáticas en
`main`, así que reescribirlas podía romper el A/B. Se comprobó cargando el
consolidado real de AF: su hoja `Inidcadores` tiene dos bloques, y el motor
usa el que trae fechas, cuyas filas son `0.993` / `0.95` / `0.9` con el rótulo
«Cumplimiento tiempos de **Solucion**» —que `ETIQUETA_INDICADOR` mapea a
«Gestión del Servicio». Resultado: `99,30%`, `95%`, `90%` y los mismos tres
nombres, carácter por carácter.

El primer bloque de esa hoja (sin fechas) sí trae `0.9` y `0.8`, y habría dado
otra cosa. No se usa, pero conviene saber que está ahí.

---

## 3. Los insumos guardados se compartían entre clientes

La persistencia de insumos (IndexedDB, con restauración automática al abrir)
ya existía. Lo que faltaba era la dimensión de cliente:

```js
const IDB_NAME = PERFIL.almacen.prefijo;   // ← se heredaba de la plantilla
```

Un cliente personalizado no declara `almacen`, así que por herencia recibía el
de su plantilla. Comprobado: `cliente-uno`, `cliente-dos` y `novaventa`
resolvían los tres a `informeNovaventa`. Como las claves dentro son solo el
tipo (`consolidado`, `glpi`…), **se pisaban entre sí**, y la restauración
automática traía al abrir el archivo del último que hubiera cargado.

**Corrección:** el prefijo declarado pertenece a quien lo declara y no se
hereda.

```js
function prefijoAlmacenInsumos(){
  return IDS_PERFILES_BASE.includes(PERFIL.id) ? PERFIL.almacen.prefijo : `informe:${PERFIL.id}`;
}
```

Los clientes base conservan el suyo (`informeAF`, `informeNovaventa`,
`informeBancoldex`) para no perder lo ya guardado en los equipos donde se
usan; cada cliente personalizado obtiene `informe:<id>`.

**Borrado.** `idbClear()` ya operaba sobre `IDB_NAME`, así que alcanza solo al
cliente activo. Se ajustaron los textos para que lo digan: el título de la
sección, el resumen de guardados, la confirmación y el aviso final nombran al
cliente.

### Sobre los datos ya guardados

Se consultó si limpiar los almacenes viejos en la migración, y la respuesta
fue que sí. **No se hizo, y conviene explicar por qué:** los insumos mezclados
viven en la base de la *plantilla*, que es también la del cliente base
(`informeNovaventa` es de Novaventa). No hay forma de distinguir qué archivo
era de Novaventa y cuál de un cliente personalizado, así que borrarla
destruiría datos legítimos de un cliente en producción.

El efecto que se buscaba se consigue igual: los clientes personalizados
arrancan con su almacén propio y vacío, sin insumos ajenos. Si además se
quiere limpiar Novaventa, el botón «Borrar informes guardados» ahora hace
exactamente eso, con Novaventa abierto y nombrándolo en la confirmación.

---

## Verificación ejecutada

**Conformidad** — 8 pruebas nuevas en tres clases:

```
Ran 82 tests — OK      (eran 74)
```

Las tres muerden: revertir cada corrección por separado deja
`test_specs_perfil_cliente` en `FAILED (failures=1)`. El archivo se restauró
idéntico tras cada mutación.

**Autopruebas del store**, en el navegador sobre el archivo real:

```
REPORTE.autopruebas()  →  31 pruebas, 0 fallos   (perfil accion-fiduciaria)
```

**End-to-end con insumos reales:**

| Comprobación | Resultado |
|---|---|
| Bancoldex, equipo limpio: c5/c6/c9/c11/c12 | `hidden: true` |
| Bancoldex, tabla de indicadores | 99,98 % · 97 % · 99 % |
| AF, tabla de indicadores tras cargar su consolidado | idéntica a los literales |
| AF, tarjetas visibles | las diez, sin cambio |
| AF, prefijo de almacén | `informeAF` |
| `cliente-uno` (extiende Novaventa) | `informe:cliente-uno` |
| Guardar en `cliente-uno`, abrir `cliente-dos` | no lo ve |
| Borrar en `cliente-dos` | `cliente-uno` conserva el suyo |

El arnés de prueba se eliminó y `localStorage` quedó limpio. Se borraron las
bases `informe:cliente-uno` y `informe:cliente-dos` creadas para la prueba.

**Efecto secundario que conviene saber:** las pruebas con Bancoldex
sobrescribieron el consolidado y los logros guardados en `informeBancoldex`
con los mismos archivos reales de junio-2026, y cambiaron el periodo guardado;
este último se restauró a julio-2026. Los GLPI y AlertsList que había ahí no
se tocaron.

---

## Pendiente

Sigue sin ejecutarse el **A/B con exports reales**. Para el punto 2 el riesgo
está acotado por la comprobación de arriba, pero el contrato pide el cotejo
formal antes de fusionar F6.
