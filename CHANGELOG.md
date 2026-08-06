# Changelog

Entradas breves, fechadas, más reciente arriba. Cada una resume una fase o
sesión ya cerrada en 3–5 líneas y enlaza al doc de sesión completo en
`docs/` para el razonamiento largo. Para lo que sigue abierto, ver
[`TASKS.md`](TASKS.md).

---

## 2026-08-06 — Reorganización del contexto documental

Se separó el plan maestro (mezclaba arquitectura estable con estado que
cambiaba cada sesión) en `docs/arquitectura-multicliente.md` (estable) +
`TASKS.md` (activo) + este changelog. Se instaló el contrato "qué leer
según la tarea" en `openspec/AGENTS.md`. Objetivo: bajar la carga por
defecto de una sesión de ~110k a ~1.500 tokens sin perder continuidad.
→ Este mismo commit.

## 2026-08-04/05 — F1: perfil de cliente como datos puros

`resolverPerfil()` + reutilización de `fusionarProfundo` global;
`REPORTE.cliente`, filtros, claves de almacén y textos de interfaz
migrados desde literales fijos. **Cerrado y fusionado en `main`** (PR #12,
commit `404408c`). Verificado: A/B con insumos reales de julio-2026, 0
diferencias (`verificar_ab.py`).
→ [`docs/2026-08-04-f1-perfil-accion-fiduciaria.md`](docs/2026-08-04-f1-perfil-accion-fiduciaria.md)

## 2026-08-04 — F0: fundación (OpenSpec, arnés A/B, dorados)

`openspec/project.md` + `AGENTS.md` (PR #11); arnés `verificar_ab.py` que
compara HTML exportados vía `window.__ESTADO__` (PR #10); mecanismo de
dorados con huellas SHA-256 sin exponer cifras de cliente (PR #14);
inventario de tarjetas recuperado del PR #5/#1 cerrado (PR #7). **Casi
completo:** falta correr contra insumos reales de junio-2026 y generar
`dorados/accion-fiduciaria-2026-06.json`.
→ [`docs/2026-08-04-f0-openspec-fundacion.md`](docs/2026-08-04-f0-openspec-fundacion.md),
[`docs/2026-08-04-f0-verificar-ab.md`](docs/2026-08-04-f0-verificar-ab.md),
[`docs/2026-08-04-f0-dorados-verificacion.md`](docs/2026-08-04-f0-dorados-verificacion.md)

---

**Pendiente de sembrar:** F2–F6 tienen trabajo avanzado en ramas sin
fusionar (`codex/f2-contrato-perfil`, `f3`, `f4`, `f5`,
`f6-perfil-novaventa`). No se agregan entradas aquí hasta que cada una se
fusione a `main` con su A/B en cero — evita registrar como hecho algo que
todavía puede cambiar. Ver [`TASKS.md`](TASKS.md) para el estado por rama.
