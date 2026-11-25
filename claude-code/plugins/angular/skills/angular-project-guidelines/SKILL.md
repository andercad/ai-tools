---
name: angular-project-guidelines
description: 'Crea o actualiza en el CLAUDE.md del proyecto el bloque "Convenciones Angular" (política de tests, a11y con base WCAG-2.2-AA, docs, i18n, verify) y las reglas de implementación y de specs que aplican en cualquier flujo, incluido /spec y /spec-impl. Usar cuando el proyecto no tiene ese bloque, el usuario pide configurar los agentes Angular para su proyecto o cambiar la política de calidad. No usar para implementar código.'
---

# Política del proyecto → `CLAUDE.md`

Claude Code carga el `CLAUDE.md` en cada sesión y en cualquier flujo (también `/spec` y `/spec-impl`); un plugin no puede aportarlo. Por eso las reglas van ahí. El agente `angular-dev` y el hook de parada leen el bloque `## Convenciones Angular`.

## Bloque a escribir (adapta las claves; borra comentarios)

````markdown
## Convenciones Angular
- tests: required | optional | none      # specs unitarios para componentes, servicios, guards, pipes, directivas nuevos
- coverage: 80                           # opcional
- a11y: WCAG-2.2-AA                      # base obligatoria; cámbiala solo si el proyecto exige otro nivel (p. ej. WCAG-2.1-AA, WCAG-2.2-AAA)
- docs: jsdoc | none                     # JSDoc en API pública (clases, métodos públicos, inputs/outputs)
- i18n: es,en | none
- workspace: app | cli-multiproject | nx
- structure: features                    # por defecto: src/app/shared + una carpeta por funcionalidad (components/ pages/ services/...); escribe otra descripción si el repo ya usa una distinta
- templates: external | inline           # external (defecto): un .html por componente, sin template inline
- verify: ng build && ng test --watch=false && ng lint

### Al implementar código Angular
Aplica siempre, también al implementar una spec:
1. Antes de escribir una pieza >30 líneas o que toque varias clases, decide en 5–8 líneas piezas, responsabilidad única, dependencias y extensión (SOLID; skill `angular-solid`). Sin capas ni abstracciones prematuras. No generes para luego rehacer.
2. Plantillas accesibles desde el principio al nivel `a11y` (base WCAG-2.2-AA, siempre): lee la skill `angular-quality-a11y` antes de escribir cualquier plantilla; semántica nativa, nombre accesible, teclado, foco, contraste y tamaño de objetivo.
3. `docs: jsdoc` → JSDoc conciso en API pública, nada sobre lo evidente.
4. `tests: required` → crea el `.spec.ts` junto a cada pieza nueva o modificada, en el mismo paso, no en un paso posterior.
5. Sintaxis y APIs de Angular: skill `angular-developer`. Solo APIs estables salvo petición o uso previo.
6. Antes de dar un paso por terminado, ejecuta `verify` y corrige. Informa qué verificaste y qué no.
7. Estructura y estilo (si `structure: features` y `templates: external`; detalle en la skill `angular-conventions`):
   - `src/app/shared/` (común y global: componentes, pipes, servicios, guards, interceptores, utils...) y una carpeta por funcionalidad con `components/`, `pages/`, `services/`, `models/`... No hay `core/`.
   - Componentes de ruta en `pages/`; reutilizables en `components/`.
   - Cada componente con su `.html` (`templateUrl`); nunca `template:` inline.
   - Alias de `tsconfig` por funcionalidad y para `shared` (`@shared/*`, `@<funcionalidad>/*`), creados antes de usarlos; imports siempre por alias.
   - Separadores `// ========== Dependencies / Inputs / Outputs / State / Computed / Lifecycle / Public methods / Private methods ==========` (solo bloques con miembros).
   - Páginas sin `@example` en el JSDoc; componentes reutilizables con `@example`.

### Al redactar specs de este proyecto
Además de lo que pida la plantilla de `/spec`, cada spec Angular incluye:
- **Diseño de clases**: piezas, responsabilidad de cada una y dependencias (SOLID).
- **Criterios de aceptación de accesibilidad** al nivel `a11y` (teclado, foco, etiquetas, contraste, tamaño de objetivo) para toda pantalla o componente con UI.
- **Plan de tests** por pieza (casos y límites) si `tests` ≠ none, e incluir su `.spec.ts` en el mismo paso del plan que la pieza.
- **Ubicación de cada pieza**: funcionalidad y carpeta (`pages/`, `components/`, `shared/...`) y alias nuevos que haya que crear.
- **Comando `verify`** como criterio de aceptación final.
````

Defaults si falta una clave: `a11y: WCAG-2.2-AA` (siempre aplica), `tests: none`, `docs: jsdoc`, `i18n: none`, `structure: features`, `templates: external`, `verify` deducible del workspace.

## Pasos
1. Lee el `CLAUDE.md`; si ya existe el bloque, actualízalo, no lo dupliques.
2. Deduce valores del repo: `package.json` (runner, scripts), `angular.json`/`nx.json`, `tsconfig*.json` (alias), `src/app`, ficheros de i18n, ESLint (`templateAccessibility`).
   Si la estructura actual de `src/app` difiere de `structure: features`, pregunta si el código nuevo sigue la nueva o se mantiene la existente (en ese caso descríbela en `structure` y elimina la regla 7 de estructura).
3. Pregunta solo lo no deducible (máx. 3): política de tests, idiomas y si el proyecto exige un nivel de accesibilidad distinto de WCAG-2.2-AA.
4. Escribe el bloque con los valores reales. Elimina las líneas de reglas que no apliquen (p. ej. i18n si es none). Añade, solo si aporta, estructura de carpetas y alias con [templates/coding-guidelines.md](templates/coding-guidelines.md) como guía.
5. Muestra el diff; no inventes datos de cliente ni de dominio.
