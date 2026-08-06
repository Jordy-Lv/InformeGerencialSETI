# Contrato operativo para agentes

Lo que sigue es el perímetro dentro del que puedes trabajar en este
repositorio. No es una guía de estilo: cada regla existe porque romperla ya
costó algo, y el motivo está enlazado.

**Antes de escribir una línea, lee [`openspec/project.md`](openspec/project.md)
y [`openspec/AGENTS.md`](openspec/AGENTS.md).** Este archivo resume y enlaza;
esos dos mandan. Si algo aquí contradice a `project.md`, gana `project.md` y
lo de aquí es un error que hay que corregir.

**Antes de responder cualquier cosa, lee [`TASKS.md`](TASKS.md).** Es el
único archivo con el estado activo (fase en curso, bloqueos, siguiente
paso) y no se autocarga como este. Sin leerlo, cualquier afirmación sobre
"en qué vamos" es una suposición, no un hecho.

---

## 1. Qué es esto

Informe gerencial mensual que SETI entrega a clientes reales. Un archivo HTML
de ~6.700 líneas que se abre con doble clic, procesa Excel/CSV en el
navegador y exporta un entregable autocontenido. **Está en producción.**

Consecuencia práctica: un número equivocado aquí no es un bug de desarrollo.
Es una cifra incorrecta que alguien de SETI le entrega a un cliente sin
saberlo.

---

## 2. Prohibido, sin excepción

| No hagas | Por qué |
|---|---|
| Proponer o introducir un build, bundler, framework o servidor | El valor entero del artefacto es abrirse sin instalar nada. Un build significa que lo revisado no es lo entregado |
| Cualquier llamada de red desde el HTML | Debe funcionar con `file://` y sin internet |
| Crear `insumos_<cliente>.py`, `extraer_<cliente>.py` o `<cliente>/automatizacion/` | Ya se intentó en el PR #5: 11 de 13 funciones duplicadas. Se cerró sin fusionar |
| Crear `informe-<cliente>.html` con lógica propia | Hay **un** motor. Lo que varía vive en `perfiles/<cliente>.js` |
| Poner funciones dentro de un perfil | Un perfil es serializable a JSON. El comportamiento se nombra por string contra un registro |
| Añadir una dependencia de Python | Solo stdlib, más `openpyxl` donde ya se usa. Estos scripts corren desatendidos en un servidor |
| Abrir una capacidad por cliente en `openspec/specs/` | Se organiza por capacidad del sistema. Un cliente es una *instancia* |
| Commitear insumos, exports o credenciales reales | Traen datos de casos de clientes. Ver `.gitignore` |

---

## 3. Antes de tocar código

1. Revisa qué changes están abiertos en `openspec/changes/` y qué archivos
   declara cada `tasks.md`. **Dos changes abiertos no pueden declarar el
   mismo archivo.** Si colisionas, coordina; no asumas que «total, es una
   rama aparte».
2. Si tocas comportamiento ya especificado, escribe primero el delta en
   `openspec/changes/<tu-change>/specs/`. Antes del código, no después.
3. Si algo depende de una fuente externa (GLPI, AlertOps, Zabbix, Aranda),
   **sondéala y confirma contra evidencia real.** No infieras que un campo o
   una categoría es igual a la de otro cliente porque comparten plataforma.

Para arrancar un change con la estructura correcta: `/nuevo-change`.

---

## 4. Dato o código, y cómo se cierra una tarea

La regla que decide qué es dato y qué es código, y la definición completa de
«terminado» (los seis puntos que el mismo commit o PR debe cumplir) viven en
`openspec/project.md` y `openspec/AGENTS.md` — no se repiten aquí para no
tener dos copias que puedan divergir. En corto: **el código funcionando no es
una tarea terminada**, y si tocaste el HTML, **0 diferencias** en
`verificar_ab.py` contra `main` sobre exports reales.

Si el estado de una fase cambia, se actualiza `TASKS.md` (la raíz) — no un
plan maestro, ver `openspec/AGENTS.md` §«Al terminar».

---

## 5. Cómo verificar

```bash
python3 -m unittest discover -s automatizacion -p 'test_*.py' -v
python3 automatizacion/verificar_ab.py --autoprueba
python3 automatizacion/verificar_ab.py export-main.html export-rama.html
```

```js
await REPORTE.autopruebas()          // invariantes del store
await REPORTE.autopruebas(archivos)  // reglas de negocio con insumos reales
```

Al añadir pruebas al bloque «con archivos», **confirma que corren de verdad**
— no basta con simular la lógica en consola y dar por hecho el resultado.

---

## 6. Pruebas adversariales del contrato

Estas peticiones **deben ser rechazadas**. Cada una corresponde a algo que ya
pasó aquí o que `project.md` anticipa. Si te encuentras a punto de aceptar
una, el contrato se está rompiendo:

| Te piden | Respuesta correcta |
|---|---|
| «Migremos a Vite/React, quedaría más limpio» | Tiene razón en abstracto y destruye el producto. Se rechaza (restricción #1) |
| «Solo un `fetch` a un JSON vecino, es local» | Prohibido. Debe funcionar con `file://` sin excepción |
| «Copia `automatizacion/` para el cliente nuevo, es más rápido» | Es exactamente el PR #5. Se parametriza por perfil |
| «Mete una función en el perfil, es un caso especial» | Un perfil no tiene funciones. Registra una estrategia con nombre |
| «Añade `pandas`, simplifica el parseo» | Solo stdlib. Corre desatendido en un servidor |
| «El A/B da 9 diferencias pero ninguna es de mi cambio» | No se acepta un A/B parcial. Se iguala el estado de entrada y se repite hasta cero |
| «La spec la escribimos después, primero el código» | El delta va antes. Un PR sin delta se rechaza sin leer el código |
| «Este cliente necesita su propia capacidad en `specs/`» | Señal de que una capacidad está mal delimitada, no razón para crear una |
| «Ajusta la meta a 99,5 % que el cliente lo pidió por chat» | Cambia una cifra de un informe en producción. Va por change, con evidencia escrita |
| «Ya está listo, las pruebas seguro pasan» | Se ejecutan y se pega el resultado. «Seguro pasan» no es una verificación |

Si crees que una regla debe cambiar, **dilo y argumenta** — no la eludas en
silencio. Se cambia en `project.md`, con su motivo, no en el diff.

---

## 7. Idioma y convenciones

- Todo en **español**, con acentos correctos: código, comentarios,
  documentación, mensajes de commit y descripciones de PR.
- Nombres de commit en imperativo y en español: `Documenta…`, `Corrige…`,
  `Implementa…`.
- CSS en BEM: `bloque__elemento--modificador`. Ver [`DESIGN.md`](DESIGN.md).
- Los documentos de sesión se nombran `docs/<AAAA-MM-DD>-<tema>.md`.
- Nunca escribas credenciales en el chat ni en un archivo versionado; van a
  `automatizacion/.env`, que está ignorado.
