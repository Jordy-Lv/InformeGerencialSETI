# Contrato operativo para agentes

Lo que sigue es el perímetro dentro del que puedes trabajar en este
repositorio. No es una guía de estilo: cada regla existe porque romperla ya
costó algo, y el motivo está enlazado.

**Antes de escribir una línea, lee [`openspec/project.md`](openspec/project.md)
y [`openspec/AGENTS.md`](openspec/AGENTS.md).** Este archivo resume y enlaza;
esos dos mandan. Si algo aquí contradice a `project.md`, gana `project.md` y
lo de aquí es un error que hay que corregir.

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

## 4. Dato o código: la regla que decide

> **Es dato** si al cambiarlo solo cambian números, etiquetas o rutas que un
> algoritmo existente ya sabe procesar.
> **Es código (estrategia registrada)** si al cambiarlo cambia *cómo se
> decide algo* o *cómo se recorre una estructura*.
> **Prueba práctica:** ¿podrías revisarlo con el líder de cuenta sin
> explicarle qué es una función? Sí → dato. No → estrategia.

**Corolario duro:** ningún mecanismo nuevo se acepta sin **dos clientes con
evidencia real** que lo necesiten. Con uno solo, es un campo opcional del
modelo canónico — no una dimensión de primera clase.

---

## 5. Cómo se cierra una tarea

El código funcionando **no** es una tarea terminada. La definición completa
está en `AGENTS.md`, sección «Al terminar». En corto, en el mismo commit o PR:

- [ ] `proposal.md`, `design.md` y `tasks.md` reflejan lo que realmente se
      implementó, incluidas decisiones nuevas y alternativas descartadas.
- [ ] El comportamiento normativo está en el delta **y** en
      `openspec/specs/<capacidad>/spec.md`, con `SHALL` + escenario.
- [ ] Existe `docs/<AAAA-MM-DD>-<tema>.md` con las secciones `Contexto`,
      `Qué se implementó`, `Verificación realizada`, `Archivos tocados` y
      `Pendiente`.
- [ ] **Cada afirmación verificable lleva al lado el comando ejecutado y su
      resultado real.** Una prueba no ejecutada se marca como pendiente,
      nunca como implícitamente aprobada.
- [ ] Si cambia el estado o el riesgo de una fase, se actualiza la tabla del
      plan maestro y el `README.md`.
- [ ] `tasks.md` y «Archivos tocados» incluyen también documentación y
      pruebas, no solo el código productivo.

Y si tocaste el HTML: **0 diferencias** en `verificar_ab.py` contra `main`,
sobre exports reales. Sin esa evidencia, la tarea no está cerrada.

---

## 6. Cómo verificar

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

## 7. Pruebas adversariales del contrato

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

## 8. Idioma y convenciones

- Todo en **español**, con acentos correctos: código, comentarios,
  documentación, mensajes de commit y descripciones de PR.
- Nombres de commit en imperativo y en español: `Documenta…`, `Corrige…`,
  `Implementa…`.
- CSS en BEM: `bloque__elemento--modificador`. Ver [`DESIGN.md`](DESIGN.md).
- Los documentos de sesión se nombran `docs/<AAAA-MM-DD>-<tema>.md`.
- Nunca escribas credenciales en el chat ni en un archivo versionado; van a
  `automatizacion/.env`, que está ignorado.
