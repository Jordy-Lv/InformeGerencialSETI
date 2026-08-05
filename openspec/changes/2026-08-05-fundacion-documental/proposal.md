# Fundación documental — contexto legible por personas e IAs

## Contexto

La auditoría del 5 de agosto de 2026 encontró que el proceso técnico se
cumple (restricciones inviolables respetadas, F1 cerrado con A/B en cero, 40
pruebas verdes), pero que **la puerta de entrada al repositorio no existe**:

- No hay `README.md`, `CLAUDE.md` ni `DESIGN.md` en la raíz.
  `openspec/project.md` se autodescribe como «la primera pantalla que
  cualquiera debe leer» y está en una subcarpeta donde nadie mira primero.
- `docs/` acumula 23 documentos sin índice. El orden cronológico no
  distingue un plan maestro vigente de una sesión de depuración superada.
- Tres changes ya fusionados (`f0-dorados`, `f1-perfil-cliente`,
  `especificar-store-reporte`) siguen en `openspec/changes/`. Eso rompe la
  regla de conjuntos de archivos disjuntos: F1 y F2 declaran los mismos
  archivos, y una IA que aplique la regla literalmente se bloquea con un
  falso positivo.
- El sistema visual del informe (225 clases CSS en nomenclatura BEM, 28
  slides de 1280×720, dos bloques de tokens) no está documentado en ninguna
  parte. Quien toque una tarjeta improvisa.
- Los siete patrones de arquitectura defendidos viven enterrados en la
  sección 4 de un plan de 37 KB, mezclados con el cronograma de fases.
- `Accion Fiduciaria/` contiene insumos y un export reales del cliente y
  **no está en `.gitignore`**, a diferencia de `Insumos*/`, `Bancoldex/` y
  `Novaventa/`, que sí lo están por la misma razón.

## Propuesta

Crear la capa de contexto que falta, sin inventar información: todo lo que
se documenta se extrae del código, de las specs o de los documentos de
sesión ya existentes.

1. **`README.md`** — punto de entrada único: qué es el producto, las tres
   restricciones inviolables, ruta de lectura según a qué vengas, estado
   real de las fases.
2. **`CLAUDE.md`** — contrato operativo para agentes: qué está prohibido,
   qué exige verificación, cómo se cierra una tarea, y una batería de
   pruebas adversariales con las que endurecer las reglas.
3. **`DESIGN.md`** — el sistema de diseño real del informe: tokens,
   nomenclatura BEM, anatomía de un slide, componentes existentes y las
   restricciones que impone `html2canvas`.
4. **`docs/README.md`** — índice del histórico con estado por documento
   (vigente / superado / referencia) y desde cuándo aplica la plantilla
   obligatoria de documento de sesión.
5. **`docs/PATRONES.md`** — los siete patrones y los descartados, extraídos
   a un lugar canónico y citables desde una revisión.
6. **`docs/requisitos-producto.md`** — los requisitos del producto que hoy
   solo existen implícitos en el código y en las specs de dos capacidades.
7. **`.gitignore`** — cubrir `Accion Fiduciaria/`.
8. **`openspec/changes/archivo/`** — fijar la convención de archivado y
   mover los tres changes ya fusionados.
9. **`.claude/skills/nuevo-change/`** — convertir el flujo de OpenSpec en
   una skill invocable, para que el proceso se ejecute en vez de leerse.

## Fuera de alcance

- Cambiar una sola línea de `informe-accion-fiduciaria 1.html`, de
  `perfiles/` o de `automatizacion/*.py`. Este change **no toca código
  productivo**, por lo que no puede alterar ninguna cifra de Acción
  Fiduciaria.
- Escribir las cinco specs de capacidad que faltan (`exportacion`,
  `inventario-tarjetas`, `adaptadores-fuente`, `automatizacion-insumos`,
  `reglas-de-negocio`). Requieren lectura y verificación del código real y
  merecen un change cada una; aquí solo se deja registrada la deuda.
- Documentar `automatizacion/instalar_tarea_programada.{ps1,bat}`: esos
  archivos todavía no están en `main`, viven sin seguimiento en la rama de
  F2 y su trazabilidad corresponde al change que los incorpore.
- Corregir los campos declarativos del perfil que el motor aún no consume
  (`metas`, `celula`, `contrato.codigo`). Aquí se documentan como deuda
  conocida; resolverlos cambia comportamiento y exige su propio change.
