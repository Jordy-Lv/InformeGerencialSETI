# F2 — Contrato desacoplado del DOM

## Contexto

F1 concentró el perfil de Acción Fiduciaria, pero seis recorridos del
pipeline todavía leen el inicio contractual desde el elemento editable
`[data-k="finicio"]`. Si ese nodo falta, se usa silenciosamente el valor
fijo `new Date(2025,8,1)`. Para otro cliente, ambos comportamientos pueden
recortar el histórico con una fecha plausible pero incorrecta.

## Propuesta

Declarar `contrato.inicio` en el perfil como fecha calendario ISO y resolverla
una vez al arrancar el motor. El pipeline y las autopruebas consumirán ese
valor validado, nunca el DOM. El campo visual de inicio se hidratará desde el
perfil para que sea una vista del dato y conserve el texto visible vigente.

## Fuera de alcance

- Cambiar las cifras, textos o comportamiento visible de Acción Fiduciaria.
- Generalizar los otros campos contractuales o las tarjetas; corresponden a
  fases posteriores si requieren comportamiento nuevo.
- Crear perfiles adicionales o modificar la automatización de insumos.
