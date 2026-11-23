---
name: angular-quality-a11y
description: Accesibilidad (WCAG-2.2-AA como base, o el nivel del proyecto) y calidad de código en Angular. Usar siempre antes de escribir plantillas o componentes con UI, al configurar ESLint/Prettier/SonarQube o reducir complejidad. No usar para sintaxis o testing con TestBed (skill angular-developer) ni para estrategia de pruebas a nivel arquitectura (agente angular-architect).
---

# Accesibilidad desde el diseño y calidad

## Accesibilidad: construir bien a la primera
Aplica al escribir la plantilla, no después:
- Elementos nativos primero (`button`, `a`, `label`, `nav`, `main`, listas); ARIA solo cuando falte semántica.
- Todo control interactivo: nombre accesible, foco visible, operable por teclado, estado expuesto (`aria-expanded`, `aria-invalid`...).
- Formularios: `label` asociado, errores vinculados con `aria-describedby` y anunciados; no solo color para indicar estado.
- Diálogos/menús: gestiona foco al abrir/cerrar y con `Esc`; usa CDK a11y o patrones de Angular ARIA (skill angular-developer, `angular-aria.md`).
- Cambio de ruta: foco y título de página actualizados. Imágenes con `alt` (vacío si decorativas).
- Nivel: WCAG-2.2-AA por defecto; si `a11y:` en el CLAUDE.md define otro, aplica ese. Incluye contraste (1.4.3/1.4.11), tamaño de objetivo (2.5.8), foco visible y no oculto (2.4.11), arrastre con alternativa (2.5.7) y entrada redundante en formularios (3.3.7).
- Verificación: `templateAccessibility` de `angular-eslint` activo (ver [accessibility.md](references/accessibility.md)).

## Calidad
- No dejes `console.log`, código muerto ni supresiones de lint sin motivo; complejidad cognitiva baja (extrae funciones).
- Ejecuta lint antes de entregar (ver [quality.md](references/quality.md) para configuración y errores frecuentes).

## Referencias
| Tema | Fichero |
|---|---|
| ARIA, formularios accesibles, foco, CDK a11y, teclado, checklist | [accessibility.md](references/accessibility.md) |
| ESLint, Prettier, SonarQube, checklist pre-PR | [quality.md](references/quality.md) |
