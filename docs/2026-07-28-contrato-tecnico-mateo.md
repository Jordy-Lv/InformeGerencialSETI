# Contrato técnico — extracción de disponibilidad de bases de datos

**Para:** Mateo Flórez Calonge (DBA)
**De:** Yordy Pardo — informe gerencial de Acción Fiduciaria
**Fecha:** 28 de julio de 2026
**Versión del esquema:** `seti.disponibilidad/1`

---

## 1. De qué se trata, en corto

Hoy el informe mensual de Acción Fiduciaria se alimenta de un consolidado de
Excel que se actualiza a mano. Queremos que la parte de disponibilidad de bases
de datos salga directamente de tu extracción.

Tu script `oracle_disponibilidad.sh` ya calcula bien lo que necesitamos. Lo que
te pido no es rehacerlo, sino **añadirle una salida en JSON** junto al HTML que
ya genera.

**Tu HTML no se va a reemplazar: consérvalo.** Es un buen informe operativo para
el equipo de bases de datos. Lo que pasa es que un informe gerencial no puede
leer un HTML de forma confiable — si algún día mueves una columna o agregas un
`<b>`, la carga se rompe sin avisar y el informe muestra el dato equivocado en
vez de un error. Con un JSON de esquema fijo eso no puede pasar: si algo no
cuadra, el informe lo rechaza y lo dice.

Son **dos archivos con dos públicos**, no una disyuntiva.

---

## 2. Periodo y zona horaria

| Concepto | Regla |
|---|---|
| **Ventana** | **Mes calendario completo.** Del día 1 a las 00:00:00 al último día a las 23:59:59 |
| **Zona horaria** | **America/Bogotá (UTC−05:00)**, sin horario de verano |
| **Denominador** | Minutos reales del mes: 43 200 en junio, 44 640 en enero, 40 320 en febrero. **No 30 días fijos** |
| **Cuándo se corre** | El primero de cada mes, para el mes que acaba de cerrar |
| **Marcas de tiempo** | ISO 8601 con desplazamiento explícito: `2026-06-30T23:59:59-05:00` |

**Cambio que hay que hacerle al script.** Hoy acepta `DIAS` y una fecha de fin, y
calcula la ventana hacia atrás. Con `./oracle_disponibilidad.sh 30 2026-06-30`
sale la ventana `2026-05-31 23:59:59 → 2026-06-30 23:59:59`: 30 días exactos,
pero desplazada un segundo y sin forma de alinearla con meses de 28 o 31 días.

Te propongo dos parámetros nuevos:

```bash
./oracle_disponibilidad.sh --desde 2026-06-01 --hasta 2026-06-30
./oracle_disponibilidad.sh --periodo 2026-06     # atajo equivalente
```

```bash
EPOCH_INI=$(date -d "${DESDE} 00:00:00" +%s)
EPOCH_FIN=$(date -d "${HASTA} 23:59:59" +%s)
MIN_TOTAL=$(awk -v a="$EPOCH_INI" -v b="$EPOCH_FIN" 'BEGIN{printf "%.0f",(b-a+1)/60}')
```

Si prefieres conservar el modo de N días para tu uso operativo, perfecto —
mientras el JSON salga siempre de una ventana calendario.

Si el `alert.log` trae la zona horaria (`COT`), el script hoy la descarta y
trata la marca como hora local del servidor. Está bien **si el servidor está en
America/Bogotá**. Confírmame que es así, por favor.

---

## 3. Qué necesitamos que extraigas

### 3.1 Alcance actual

Las cinco instancias que ya tienes en `INCLUIR`, con el nombre de CI que usa el
cliente:

| SID en el servidor | CI en el informe | Motor |
|---|---|---|
| `INVERACCION` | `INVERACCION` | Oracle |
| `ACBACOLG` | `ACBACOLG` | Oracle |
| `APPACCION` | `APPACCION` | Oracle |
| `INVHIST` | **`INVHISTO`** | Oracle |
| `cheeta` | **`CHEETA`** | Oracle |

Tu bloque `ETIQUETA` ya hace exactamente esta traducción — solo hay que llevarla
al JSON. **El campo `ci` es el que manda para el informe**; `sid` viaja al lado
para trazabilidad.

`cheetaNEW` sigue excluida.

### 3.2 Por instancia y periodo

1. Minutos totales del periodo (el denominador).
2. Minutos de indisponibilidad dentro del periodo.
3. Porcentaje de disponibilidad.
4. Estado de la instancia al momento de la extracción (arriba / caída).
5. Cobertura del `alert.log` (completa / parcial) — el mismo indicador que ya
   calculas.
6. El detalle de cada ventana de caída: inicio, fin, minutos y origen
   (`REAL` / `ESTIMADA` / `NO_REABRIO`).

Todo esto ya lo calcula tu script. Es un cambio de formato de salida, no de
lógica.

### 3.3 Lo que aún no sabemos, y por qué no te lo pido todavía

El consolidado tiene **dos** columnas de disponibilidad por motor,
«Disponibilidad Real» y «Disponibilidad SETI», y para Oracle dicen esto:

| | nov-25 | ene-26 | feb-26 |
|---|---|---|---|
| **Real** | 98,02 % | 100 % | **97,32 %** |
| **SETI** | 98,02 % | **99,93 %** | 100 % |

La lectura más razonable es que **SETI = Real menos las caídas no imputables a
SETI**: la de noviembre cuenta en las dos, y la de febrero se excluye de la
columna contractual. Eso encaja.

Lo que no encaja es enero, donde SETI sale *peor* que Real, lo cual es
imposible bajo esa regla. Y hay evidencia de dónde está el error: **la caída de
enero sí ocurrió** — aparece como 0,9993 en la hoja `Disponibilidad` (CHEETA) y
en la hoja `Inidcadores`. Tres hojas la registran y la tabla «Real» no. Parece
que a esa tabla se le olvidó el evento de enero.

Te lo cuento porque si mides enero con tu script vas a encontrar la caída de
CHEETA, y quiero que sepas de antemano que el Excel te va a contradecir en esa
celda — no es un error tuyo.

**Por ahora entrega solo `disponibilidad_real`**: el porcentaje crudo del
`alert.log`, sin excluir nada. Deja `disponibilidad_seti` en `null`. Cuando
tengamos el calendario de ventanas de mantenimiento lo implementamos, y lo
natural sería un archivo de exclusiones que el script lea, con la ventana y su
motivo, para que quede auditable quién excluyó qué.

Si tú ya sabes cómo se decide hoy qué caída entra en cada columna, me ahorras la
consulta.

---

## 4. Qué se calcula dónde

La regla es simple: **tú entregas hechos medidos; el informe aplica las reglas de
negocio.**

Así no hay dos implementaciones de lo mismo. Si el día de mañana el cliente
renegocia la meta o cambia el número de decimales, se toca un solo lado.

| Cálculo | Dónde | Por qué |
|---|---|---|
| Detección de arranques y paradas | **Script** | Solo el `alert.log` lo sabe |
| Minutos de caída, recortados al periodo | **Script** | Ídem |
| % de disponibilidad **por instancia** | **Script** | Determinista y verificable contra el detalle |
| Marca de cobertura del log | **Script** | Solo el script sabe dónde empieza el archivo |
| Promedio entre CI | **Informe** | Ya implementado y con pruebas |
| Comparación contra la meta | **Informe** | `cumpleMeta()` — regla acordada con negocio |
| Redondeo publicado | **Informe** | 1 decimal, decisión de Santiago Amaya del 23/07/2026 |
| Veredicto CUMPLE / REVISAR | **Informe** | No lo pongas en el JSON |
| Colores, gráficas, narrativa | **Informe** | — |

**En concreto: no incluyas `cumple`, `estado_contractual` ni la meta aplicada.**
Ponemos `meta` en los metadatos solo como referencia de con qué se corrió, no
para que el informe la use.

Sobre el promedio general: el tuyo es promedio simple entre bases y está bien
para tu informe. **No lo uses como fuente del informe gerencial** — ese promedio
lo calculamos nosotros sobre los 14 CI del cliente, no sobre las 5 Oracle.

---

## 5. Formato de salida

### 5.1 Nombre y ubicación

```
disponibilidad-<motor>-<AAAA-MM>.json
```

Ejemplo: `disponibilidad-oracle-2026-06.json`

Se deposita en la carpeta del mes, dentro de la biblioteca sincronizada que ya
usamos:

```
<RUTA_INTAKE_BD>/
  └── 2026-06/
        ├── disponibilidad-oracle-2026-06.json     ← el que consume el informe
        └── disponibilidad_oracle_20260630.html    ← el tuyo, para el equipo DBA
```

Te paso la ruta exacta cuando la confirmemos. Si te queda más cómodo dejarlo en
el servidor y que nosotros lo recojamos por `scp`, también sirve — dime qué
prefieres.

**El archivo se sobrescribe si se vuelve a correr el mismo periodo.** El
histórico lo conserva la carpeta del mes, no el nombre.

### 5.2 Esquema

```json
{
  "esquema": "seti.disponibilidad/1",
  "generado": "2026-07-01T01:07:22-05:00",
  "zona_horaria": "America/Bogota",
  "cliente": "Acción Fiduciaria",
  "motor": "Oracle",
  "periodo": {
    "clave": "2026-06",
    "anio": 2026,
    "mes": 6,
    "desde": "2026-06-01T00:00:00-05:00",
    "hasta": "2026-06-30T23:59:59-05:00",
    "minutos": 43200
  },
  "fuente": {
    "tipo": "alert.log",
    "servidor": "seti-ora-prod-01",
    "script": "oracle_disponibilidad.sh",
    "version": "2.0",
    "meta_referencia": 99.30
  },
  "instancias": [
    {
      "ci": "INVERACCION",
      "sid": "INVERACCION",
      "motor": "Oracle",
      "estado_actual": "ARRIBA",
      "minutos_periodo": 43200,
      "minutos_caida": 0.0,
      "disponibilidad_real": 100.00,
      "disponibilidad_seti": null,
      "cobertura_log": "COMPLETA",
      "calidad": "OK",
      "eventos": []
    },
    {
      "ci": "CHEETA",
      "sid": "cheeta",
      "motor": "Oracle",
      "estado_actual": "ARRIBA",
      "minutos_periodo": 44640,
      "minutos_caida": 31.2,
      "disponibilidad_real": 99.93,
      "disponibilidad_seti": null,
      "cobertura_log": "COMPLETA",
      "calidad": "OK",
      "eventos": [
        {
          "inicio": "2026-01-18T02:14:00-05:00",
          "fin": "2026-01-18T02:45:12-05:00",
          "minutos": 31.2,
          "origen": "REAL"
        }
      ]
    }
  ]
}
```

### 5.3 Campos, uno por uno

**Raíz**

| Campo | Tipo | Oblig. | Formato / valores | Ejemplo |
|---|---|---|---|---|
| `esquema` | texto | **sí** | literal `seti.disponibilidad/1` | `"seti.disponibilidad/1"` |
| `generado` | texto | **sí** | ISO 8601 con offset — cuándo corrió la extracción | `"2026-07-01T01:07:22-05:00"` |
| `zona_horaria` | texto | **sí** | nombre IANA | `"America/Bogota"` |
| `cliente` | texto | **sí** | literal `Acción Fiduciaria` (con tilde, UTF-8) | |
| `motor` | texto | **sí** | uno de: `Oracle`, `SQL`, `Mysql`, `Aws` — **exactamente esa capitalización** | `"Oracle"` |
| `periodo` | objeto | **sí** | ver abajo | |
| `fuente` | objeto | **sí** | ver abajo | |
| `instancias` | lista | **sí** | puede venir vacía, pero la clave debe existir | |

**`periodo`**

| Campo | Tipo | Oblig. | Notas |
|---|---|---|---|
| `clave` | texto | **sí** | `AAAA-MM` |
| `anio` | entero | **sí** | 4 dígitos |
| `mes` | entero | **sí** | **1–12** (enero = 1). El informe convierte a base 0 internamente; tú manda 1–12 |
| `desde` | texto | **sí** | ISO 8601 con offset, día 1 a las 00:00:00 |
| `hasta` | texto | **sí** | ISO 8601 con offset, último día a las 23:59:59 |
| `minutos` | entero | **sí** | minutos reales del mes |

**`fuente`**

| Campo | Tipo | Oblig. | Notas |
|---|---|---|---|
| `tipo` | texto | **sí** | `alert.log` |
| `servidor` | texto | **sí** | `hostname` |
| `script` | texto | **sí** | nombre del script |
| `version` | texto | **sí** | súbela cuando cambies la lógica de cálculo |
| `meta_referencia` | número | no | informativo; el informe usa la suya |

**Cada elemento de `instancias`**

| Campo | Tipo | Oblig. | Formato / valores |
|---|---|---|---|
| `ci` | texto | **sí** | nombre canónico del CI, tabla §3.1. **Es la clave de emparejamiento** |
| `sid` | texto | **sí** | SID real en el servidor, tal cual |
| `motor` | texto | **sí** | mismo valor que el de la raíz |
| `estado_actual` | texto | **sí** | `ARRIBA` \| `CAIDA` \| `DESCONOCIDO` |
| `minutos_periodo` | entero | **sí** | = `periodo.minutos` |
| `minutos_caida` | número | **sí** | 1 decimal. `0.0` si no hubo caídas |
| `disponibilidad_real` | número o `null` | **sí** | **escala 0–100, 2 decimales.** Ver §5.4 |
| `disponibilidad_seti` | número o `null` | **sí** | `null` por ahora (§3.3) |
| `cobertura_log` | texto | **sí** | `COMPLETA` \| `PARCIAL` |
| `calidad` | texto | **sí** | `OK` \| `SIN_ALERT` \| `SIN_DATO` |
| `eventos` | lista | **sí** | `[]` si no hubo caídas |

**Cada elemento de `eventos`**

| Campo | Tipo | Oblig. | Formato |
|---|---|---|---|
| `inicio` | texto | **sí** | ISO 8601 con offset, ya recortado al periodo |
| `fin` | texto | **sí** | ídem |
| `minutos` | número | **sí** | 1 decimal |
| `origen` | texto | **sí** | `REAL` \| `ESTIMADA` \| `NO_REABRIO` |

### 5.4 Porcentajes — la regla más importante

> **Escala 0–100, número JSON, 2 decimales. Nunca fracción, nunca cadena, nunca
> con el signo `%`.**

| Correcto | Incorrecto | Por qué |
|---|---|---|
| `100.00` | `1` | el informe interpreta valores ≤ 1,01 como fracción |
| `99.93` | `0.9993` | ídem |
| `98.02` | `"98,02%"` | tiene que ser número, no texto |
| `0.00` | `0` con otro significado | `0.00` = caída total |
| `null` | `0` cuando no se pudo medir | son cosas distintas (§5.5) |

El punto crítico es el **`1`**: si mandas `1` queriendo decir 1 %, el informe lo
publica como **100 %**. Por eso la escala 0–100 no es negociable.

Usa punto decimal, no coma. `printf "%.2f"` te lo da bien.

### 5.5 Nulos, errores y ausencias

| Situación | `disponibilidad_real` | `calidad` | `minutos_caida` | Qué hace el informe |
|---|---|---|---|---|
| Todo bien | número 0–100 | `OK` | número | Publica el valor |
| No se pudo leer el `alert.log` | `null` | `SIN_ALERT` | `null` | Muestra «sin dato», **no 0 ni 100**; excluye del promedio |
| Instancia caída todo el mes | `0.00` | `OK` | = minutos del mes | Publica 0 %, en rojo |
| `alert.log` no cubre todo el periodo | número | `OK` | número | Publica con marca de cobertura parcial |
| Instancia dada de baja | **no la incluyas** | — | — | La ausencia se detecta contra los CI esperados |

**`null` significa «no lo pude medir». `0` significa «estuvo caída».** Nunca uses
uno por el otro: un `0` inventado convierte un fallo de la herramienta en un
incumplimiento contractual del cliente, y un `100` inventado esconde una caída
real. Tu script ya lo hace bien excluyendo las `SIN_ALERT` del promedio — es
exactamente el criterio.

**Si la extracción falla entera** (el servidor no responde, no hay ninguna
instancia): **no escribas el archivo.** Un archivo ausente es una señal clara; un
archivo con ceros es una mentira. El informe avisa que falta la fuente y esa
sección sigue siendo manual, sin afectar a las demás.

Devuelve código de salida distinto de cero para que la tarea programada lo
detecte.

### 5.6 Codificación

- **UTF-8 sin BOM.**
- JSON válido: comillas dobles, sin comas finales, sin comentarios.
- Escapa lo que haya que escapar. `Acción` puede ir literal en UTF-8 o como
  `Acción`.
- Verifica antes de publicar:

```bash
python3 -m json.tool disponibilidad-oracle-2026-06.json > /dev/null && echo "JSON válido"
```

### 5.7 Emisor sugerido en Bash

Para que no tengas que pelear con el escapado. La idea es acumular las filas ya
formateadas y armar el objeto al final:

```bash
# Escapa una cadena para JSON
json_str() {
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\t/\\t/g'
}

# Número o null
json_num() {
    [ -z "$1" ] || [ "$1" = "-" ] && { printf 'null'; return; }
    printf '%s' "$1"
}

{
  printf '{\n'
  printf '  "esquema": "seti.disponibilidad/1",\n'
  printf '  "generado": "%s",\n' "$(date '+%Y-%m-%dT%H:%M:%S%:z')"
  printf '  "zona_horaria": "America/Bogota",\n'
  printf '  "cliente": "Acción Fiduciaria",\n'
  printf '  "motor": "Oracle",\n'
  printf '  "periodo": {"clave":"%s","anio":%d,"mes":%d,"desde":"%s","hasta":"%s","minutos":%d},\n' \
         "$CLAVE" "$ANIO" "$MES" "$DESDE_ISO" "$HASTA_ISO" "$MIN_TOTAL"
  printf '  "fuente": {"tipo":"alert.log","servidor":"%s","script":"oracle_disponibilidad.sh","version":"2.0","meta_referencia":%s},\n' \
         "$(json_str "$HOST")" "$META"
  printf '  "instancias": [\n'
  sep=""
  while IFS='|' read -r sid est minc disp cob estado ruta; do
      [ -z "$sid" ] && continue
      ci=$(etiqueta_ci "$sid")
      if [ "$est" = "SIN_ALERT" ]; then
          calidad="SIN_ALERT"; d="null"; m="null"
      else
          calidad="OK"; d=$(json_num "$disp"); m=$(json_num "$minc")
      fi
      printf '%s    {"ci":"%s","sid":"%s","motor":"Oracle","estado_actual":"%s",' \
             "$sep" "$(json_str "$ci")" "$(json_str "$sid")" "$estado"
      printf '"minutos_periodo":%d,"minutos_caida":%s,' "$MIN_TOTAL" "$m"
      printf '"disponibilidad_real":%s,"disponibilidad_seti":null,' "$d"
      printf '"cobertura_log":"%s","calidad":"%s","eventos":[' \
             "${cob:-COMPLETA}" "$calidad"
      esep=""
      if [ -s "$TMP/detalle_$sid.txt" ]; then
          while IFS='|' read -r a b mm o; do
              printf '%s{"inicio":"%s","fin":"%s","minutos":%s,"origen":"%s"}' \
                     "$esep" "$(iso "$a")" "$(iso "$b")" "$mm" "$(slug_origen "$o")"
              esep=","
          done < "$TMP/detalle_$sid.txt"
      fi
      printf ']}\n'
      sep="    ,"
  done < "$TMP/resumen.txt"
  printf '  ]\n}\n'
} > "$JSON"
```

Dos detalles: `iso()` convierte tus `%Y-%m-%d %H:%M:%S` a ISO con offset
(`date -d "$1" '+%Y-%m-%dT%H:%M:%S%:z'`), y `slug_origen()` pasa `NO REABRIO` a
`NO_REABRIO` (sin espacio, que es lo que valida el esquema).

Adáptalo como quieras — lo que importa es el resultado, no el código.

---

## 6. Cómo lo carga el informe

No necesitas hacer nada de esto; te lo cuento para que sepas dónde termina tu
archivo y por qué pido lo que pido.

```
tu script  ──►  disponibilidad-oracle-2026-06.json
                        │
                        ▼
        extraer_disponibilidad.py  (lo escribimos nosotros)
          · valida esquema, periodo y cliente
          · calcula SHA-256 del contenido
                        │
                        ▼
              insumos-af.js   {archivos: {glpi, alertas, disponibilidad}}
                        │
                        ▼  copiado junto al HTML por la tarea mensual
              informe-accion-fiduciaria.html
                        │
                        ▼  al abrirlo: verifica versión, periodo y huella
                    se carga solo
```

Tres cosas que esto implica:

- **La huella SHA-256 se calcula de tu archivo tal como llega.** Si alguien lo
  edita después, el informe lo rechaza y avisa. No es desconfianza hacia ti: es
  que ese archivo se carga sin que nadie lo apruebe, y tiene que poder demostrar
  que es el que salió de tu extracción.
- **El periodo lo manda tu archivo, no el desplegable del informe.** Por eso
  `periodo` es obligatorio: evita que alguien abra un corte de junio creyendo que
  es de julio.
- **Si tu fuente falta o no valida, las demás se cargan igual** y esa sección
  vuelve a ser manual. Nada bloquea a nada.

---

## 7. Criterios de aceptación

Damos el trabajo por bueno cuando pasa esto:

### 7.1 Formato

- [ ] `python3 -m json.tool` valida el archivo sin error.
- [ ] `esquema` es exactamente `seti.disponibilidad/1`.
- [ ] Están las 5 instancias con su `ci` canónico (`INVHISTO` y `CHEETA`
      traducidos, no `INVHIST` ni `cheeta`).
- [ ] Todos los porcentajes en escala 0–100. Ninguno entre 0 y 1,01 salvo que
      sea una caída real de esa magnitud.
- [ ] `periodo.minutos` coincide con los minutos reales del mes.
- [ ] Ninguna instancia con `disponibilidad_real: 0` que debiera ser `null`.
- [ ] UTF-8 sin BOM; `Acción Fiduciaria` se lee bien.

### 7.2 Reconciliación contra el Excel actual

Esta es la prueba de verdad. Corre la extracción para **cuatro meses** y compara
contra el consolidado. Ya audité el archivo, así que te paso los valores exactos
contra los que vamos a contrastar:

| Mes | CI | Excel dice | Tu JSON debería dar | Qué prueba |
|---|---|---|---|---|
| **jun-26** | los 5 | 100,00 % | `100.00`, `minutos_caida: 0.0` | El caso normal — **pero ojo, ver abajo** |
| **may-26** | los 5 | 100,00 % | `100.00` | Reproducibilidad |
| **nov-25** | los 5 | **98,02 %** | `98.02` ≈ **855 min** (14 h 15 min) sobre 43 200 | **La prueba clave** |
| **ene-26** | CHEETA | **99,93 %** | `99.93` ≈ **31 min** sobre 44 640 | Atribución por instancia |
| **ene-26** | los otros 4 | 100,00 % | `100.00` | Que la caída no se contagie |

**Nov-25 es la que más importa.** Es el único mes con un evento grande y afecta a
las cinco instancias por igual. Si tu script reproduce 98,02 % en las cinco, el
método coincide con el del Excel y podemos automatizar con confianza. Si da otro
número, habremos encontrado en qué difieren las dos definiciones — que también es
un resultado útil, y prefiero descubrirlo ahora.

> ### ⚠️ Junio ya tiene una contradicción, y es el mejor caso de prueba
>
> El consolidado dice que **CHEETA estuvo al 100,00 % en junio de 2026**.
>
> Pero el informe mensual de Oracle de ese mismo período
> (`Informe_Mensual_Oracle_AcFiduciaria_Junio2026_v3_1.docx`, sección 1) dice:
> *«La base de datos CHEETA tiene un uptime de 14.57 días, mientras que las demás
> superan los 102 días de operación continua.»*
>
> Un uptime de 14,57 días medido a fin de junio sitúa un **reinicio de CHEETA
> alrededor del 16 de junio**. Un reinicio implica minutos de indisponibilidad,
> así que el 100,00 % del Excel y el uptime del informe no pueden ser ambos
> correctos — salvo que ese reinicio fuera una ventana de mantenimiento acordada
> y por eso se excluyera.
>
> **Es exactamente la pregunta que tu script puede responder.** Cuando corras
> junio, el `alert.log` de CHEETA debería mostrar ese arranque. Lo que salga nos
> dice tres cosas de una vez: cuántos minutos fue, si el Excel lo omitió o lo
> excluyó a propósito, y si «Real» y «SETI» se distinguen por ventanas de
> mantenimiento. **Si solo puedes correr un mes, corre junio y mira CHEETA.**

Dos advertencias más:

- **Nov-25 puede estar fuera de la retención de tu `alert.log`.** Si es así,
  debería salir con `cobertura_log: "PARCIAL"`. Ese solo hecho ya nos dice cuánta
  historia podemos reconstruir. No lo fuerces; repórtalo.
- **Los `alert.log` no son todos del mismo formato.** CHEETA, ACBACOLG y
  APPACCIO corren Oracle 10.2.0.5 y INVHIST e INVERACC 12.2.0.1, así que vas a
  encontrar el formato `ctime` y el formato ISO en la misma corrida. Tu parser ya
  reconoce los dos — solo confirma que ninguna instancia sale con
  `minutos_caida: 0` por no haber reconocido ninguna fecha.

Tolerancia: **±0,01 puntos porcentuales**. Una diferencia mayor no es
necesariamente un error tuyo — puede ser que el Excel se calcule de otra forma.
Lo miramos juntos.

### 7.3 Robustez

- [ ] Una instancia sin `alert.log` legible sale con `calidad: "SIN_ALERT"` y
      `disponibilidad_real: null`, y **no** rompe a las demás.
- [ ] Correr dos veces el mismo periodo produce el mismo resultado (salvo
      `generado`).
- [ ] Si falla todo, **no** se escribe el archivo y el código de salida es ≠ 0.
- [ ] Un mes de 28 y uno de 31 días producen `periodo.minutos` distintos y
      correctos.

---

## 8. Cosas que no sabemos todavía

No hace falta que las resuelvas tú — las estoy consultando con el líder de
cuenta. Te las cuento porque puede que tengas la respuesta a mano y nos ahorres
la vuelta:

1. **¿Existe un calendario formal de ventanas de mantenimiento?** ¿Dónde vive y
   quién lo aprueba? Es lo que nos falta para saber qué se descuenta de la
   columna SETI.
2. **El reinicio de CHEETA de mediados de junio (§7.2): ¿fue una ventana
   programada?** Si lo fue, ya tenemos media respuesta a la pregunta anterior.
3. **Los otros 9 CI del cliente** (PWP, PSE, ACCIONAR, INTRANET, ORFEO, ACCION,
   CORETUTASK, LEGALBC, VLOZ): ¿qué motor y qué servidor son? ¿Los administras
   tú también? Te lo pregunto porque en el consolidado **llevan 18 meses en
   100,00 % exacto, sin una sola variación** — o son muy estables, o nadie los
   está midiendo.
4. **¿El servidor PUMA está en America/Bogotá?**
5. **¿Qué retención tiene el `alert.log`?** Define hasta dónde podemos
   reconstruir historia.

Y tres preguntas que pueden cambiar bastante el plan:

6. **El Grafana que dispara las alertas a AlertOps: ¿qué tiene detrás?** Todas
   las alertas del cliente entran con `IntegrationName: Grafana`, y en junio
   fueron 49 de `Tipo: oracle` y 4 de `Tipo: sqlserver` — o sea que **ya cubre
   SQL Server además de Oracle**. Si hay un Prometheus o similar guardando
   series, quizá la disponibilidad de **los 14 CI** salga de una sola consulta,
   con la misma definición para todos los motores, y nos ahorramos escribir un
   script por tecnología. Me interesa mucho tu opinión sobre esto.

7. **El informe mensual de Oracle que ya entregan.** Revisando los insumos me
   encontré con `Informe_Mensual_Oracle_AcFiduciaria_Junio2026_v3_1.docx`, y
   resulta que **ya contiene datos que hoy alguien transcribe a mano al
   consolidado**: la ocupación de los filesystems (comprobé que
   `/u02/data/inverdata03` al 94 % coincide celda por celda con la hoja
   `Capacidad`) y la política y el estado de los jobs RMAN. ¿Cómo se genera ese
   informe? Si sale de consultas, esas mismas consultas podrían emitir el JSON y
   nos ahorraríamos dos hojas enteras del Excel.

8. **Backups.** El consolidado tiene 14 instancias × 19 meses de porcentaje de
   respaldo, y **las 266 celdas dicen 100 %**. Mientras tanto tu informe mensual
   advierte que `/mnt/BACKUP_DBO` está al 91 %. ¿Se podría sacar el estado real
   de `RC_RMAN_BACKUP_JOB_DETAILS` con este mismo contrato? Sería el siguiente
   paso natural.

---

## 9. Resumen

| | |
|---|---|
| **Qué entregas** | `disponibilidad-oracle-AAAA-MM.json`, esquema `seti.disponibilidad/1` |
| **Cuándo** | El primero de cada mes, para el mes que cerró |
| **Ventana** | Mes calendario completo, America/Bogotá |
| **Porcentajes** | Escala **0–100**, número, 2 decimales |
| **Sin dato** | `null` + `calidad: "SIN_ALERT"` — nunca `0`, nunca `100` |
| **Falla total** | No escribas el archivo; código de salida ≠ 0 |
| **Tu HTML** | Consérvalo, es útil. Simplemente no es la vía de integración |
| **Prueba clave** | Reproducir **98,02 %** en nov-25 para las 5 instancias |
| **Si solo corres un mes** | **Junio, mirando CHEETA** — el uptime de tu propio informe contradice el 100 % del Excel |

Cualquier cosa del esquema que te resulte incómoda de generar, dímelo y lo
ajustamos. Lo único que de verdad no puede moverse es la escala 0–100 y la
distinción entre `null` y `0`.

Gracias, Mateo — el script está muy bien hecho y esto es sobre todo cambiarle la
salida.
